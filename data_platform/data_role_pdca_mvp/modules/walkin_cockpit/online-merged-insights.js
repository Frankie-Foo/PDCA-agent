/**
 * 线上驾驶舱核心块并入 Walk-in「客流分析」：OKR 表、渠道线索、区域堆叠、客户来源对比。
 * 数据：data/online_channel_reference.json（结构与 Excel 渠道表一致）；客户来源来自当前代理商汇总。
 */
(function (global) {
  'use strict';

  var ref = null;
  var vnRef = null;
  var loadPromise = null;

  function fmtNum(x) {
    return Number(x).toLocaleString('zh-CN', { maximumFractionDigits: 1 });
  }

  function sum(arr, fn) {
    var t = 0;
    for (var i = 0; i < arr.length; i++) t += fn(arr[i]);
    return t;
  }

  /** @param {string} s */
  function hashStr(s) {
    var h = 0;
    for (var i = 0; i < s.length; i++) h = ((h << 5) - h + s.charCodeAt(i)) | 0;
    return Math.abs(h);
  }

  /**
   * VERTU 介绍客户业绩（mock，按门店+月份稳定随机）
   * @param {string} nm
   * @param {number} realSal
   * @param {string} monthKey
   */
  function mockVertuSales(nm, realSal, monthKey) {
    if (!realSal || realSal <= 0) return 0;
    var h = hashStr(nm + '|' + monthKey);
    var share = 0.06 + (h % 19) / 100;
    return Math.round(realSal * share * 10) / 10;
  }

  /** @param {string} rg @param {string} nm */
  function dealerRegionStoreLabel(rg, nm) {
    return (rg || '—') + ' · ' + (nm || '—');
  }

  function scaleFactor(monthKey) {
    if (!ref || !ref.scaleByMonth) return 1;
    if (ref.scaleByMonth[monthKey] != null) return ref.scaleByMonth[monthKey];
    return 1;
  }

  function scaledStores(monthKey) {
    if (!ref || !ref.stores) return [];
    var f = scaleFactor(monthKey);
    return ref.stores.map(function (r) {
      if (r.hk) {
        return {
          rg: r.rg,
          nm: r.nm,
          mgr: r.mgr,
          hk: 1,
          Ls: 0,
          Ll: 0,
          Lo: 0,
          sal: 0,
        };
      }
      return {
        rg: r.rg,
        nm: r.nm,
        mgr: r.mgr,
        hk: 0,
        Ls: Math.max(0, Math.round(r.Ls * f)),
        Ll: Math.max(0, Math.round(r.Ll * f)),
        Lo: Math.max(0, Math.round(r.Lo * f)),
        sal: Math.round(r.sal * f * 10) / 10,
      };
    });
  }

  function mainland(rows) {
    return rows.filter(function (r) {
      return !r.hk;
    });
  }

  function okrMonthly(nm, monthKey) {
    var M = (ref && ref.okrByMonth && ref.okrByMonth[monthKey]) || null;
    if (!M && ref && ref.okrByMonth) {
      var keys = Object.keys(ref.okrByMonth);
      M = ref.okrByMonth[keys[keys.length - 1]];
    }
    if (!M) return 0;
    return M[nm] != null ? M[nm] : 0;
  }

  function aggRegions(ml) {
    var order = (ref && ref.regionOrder) || ['北区', '西区', '东区', '南区'];
    var out = [];
    for (var i = 0; i < order.length; i++) {
      var rg = order[i];
      var L = ml.filter(function (x) {
        return x.rg === rg;
      });
      if (!L.length) continue;
      var Ls = sum(L, function (x) {
        return x.Ls;
      });
      var Ll = sum(L, function (x) {
        return x.Ll;
      });
      var Lo = sum(L, function (x) {
        return x.Lo;
      });
      out.push({ rg: rg, Ls: Ls, Ll: Ll, Lo: Lo, ld: Ls + Ll + Lo });
    }
    return out;
  }

  function customerOwnershipFromDealers(dealerStores) {
    var own = 0;
    var vertu = 0;
    (dealerStores || []).forEach(function (s) {
      var eff = Number(s.effectiveCustomers) || 0;
      var people = Number(s.walkinPeople) || 0;
      own += eff;
      vertu += Math.max(0, people - eff);
    });
    if (own <= 0 && vertu <= 0 && dealerStores && dealerStores.length) {
      own = sum(dealerStores, function (x) {
        return Number(x.wechatAddCount) || 0;
      });
      vertu = sum(dealerStores, function (x) {
        return Math.max(0, (Number(x.walkinPeople) || 0) - (Number(x.wechatAddCount) || 0));
      });
    }
    return { own: own, vertu: vertu };
  }

  function barUnit(tag, val, mx, cls, unit) {
    unit = unit || '条';
    var pct = Math.round((val / mx) * 130);
    return (
      '<div class="oi-bar-unit">' +
      '<div class="oi-bar-tag">' +
      val +
      ' ' +
      unit +
      '</div>' +
      '<div class="oi-bar-track"><div class="oi-bar-fill ' +
      cls +
      '" style="height:' +
      pct +
      'px"></div></div>' +
      '<div class="oi-bar-cap">' +
      tag +
      '</div></div>'
    );
  }

  function renderOkrTable(ml, monthKey) {
    var est = (ref && ref.estRatio) || 4;
    var tb = '';
    var sumOkr = 0;
    var sumSal = 0;
    var sumVertu = 0;
    for (var i = 0; i < ml.length; i++) {
      var r = ml[i];
      var okr = okrMonthly(r.nm, monthKey);
      var realSal = r.sal;
      var vertuSal = mockVertuSales(r.nm, realSal, monthKey);
      sumOkr += okr;
      sumSal += realSal;
      sumVertu += vertuSal;
      var completion = okr > 0 ? Math.round((realSal / okr) * 1000) / 10 : null;
      var vertuShare =
        realSal > 0 ? Math.round((vertuSal / realSal) * 1000) / 10 : null;
      var diff =
        completion != null ? Math.round((completion - est) * 10) / 10 : null;
      tb +=
        '<tr><td>' +
        r.rg +
        '</td><td class="text-left">' +
        dealerRegionStoreLabel(r.rg, r.nm) +
        '</td><td class="num">' +
        fmtNum(okr) +
        '</td><td class="num">' +
        fmtNum(realSal) +
        '</td><td class="num">' +
        (completion != null ? completion + '%' : '—') +
        '</td><td class="num">' +
        fmtNum(vertuSal) +
        '</td><td class="num">' +
        (vertuShare != null ? vertuShare + '%' : '—') +
        '</td><td class="num">' +
        est +
        '%</td><td class="num ' +
        (diff != null && diff >= 0 ? 'oi-delta-ok' : '') +
        '">' +
        (diff != null ? (diff >= 0 ? '+' : '') + diff + '%' : '—') +
        '</td></tr>';
    }
    var aggCompletion = sumOkr > 0 ? Math.round((sumSal / sumOkr) * 1000) / 10 : 0;
    var aggVertuShare =
      sumSal > 0 ? Math.round((sumVertu / sumSal) * 1000) / 10 : 0;
    var foot =
      ml.length +
      ' 家经销商·门店 · OKR 合计 ' +
      fmtNum(sumOkr) +
      ' 万 · 真实销售 ' +
      fmtNum(sumSal) +
      ' 万 · 加权完成率 ' +
      aggCompletion +
      '% · VERTU 介绍业绩(mock) ' +
      fmtNum(sumVertu) +
      ' 万 · 占真实销售 ' +
      aggVertuShare +
      '%';
    return { tbody: tb, foot: foot };
  }

  function renderChannelBars(ml) {
    var a = sum(ml, function (x) {
      return x.Ls;
    });
    var b = sum(ml, function (x) {
      return x.Ll;
    });
    var c = sum(ml, function (x) {
      return x.Lo;
    });
    var mx = Math.max(a, b, c, 1);
    return (
      barUnit('短视频', a, mx, 'a', '条') +
      barUnit('直播', b, mx, 'b', '条') +
      barUnit('其他', c, mx, 'c', '条')
    );
  }

  function renderCustomerBars(own, vertu) {
    var mx = Math.max(own, vertu, 1);
    return (
      barUnit('自有有效客户', own, mx, 'b', '人') + barUnit('VERTU 推送', vertu, mx, 'd', '人')
    );
  }

  /**
   * 区域汇总表：短视频/直播/线索/真实销售/完成率均 mock（按区域+月稳定）
   * @param {string} rg
   * @param {number} storeCount
   * @param {string} monthKey
   * @param {number} scale
   */
  function mockRegionMetrics(rg, storeCount, monthKey, scale) {
    var h = hashStr(rg + '|' + monthKey);
    var n = Math.max(1, storeCount);
    var sv = Math.round(n * (68 + (h % 28)) * scale);
    var lv = Math.round(n * (7 + ((h >> 4) % 7)) * scale);
    var ld = Math.round(sv * (0.78 + (h % 15) / 100) + lv * 2.2);
    var sal = Math.round(n * (48 + (h % 35)) * scale * 10) / 10;
    var avgCompletion = Math.round((3.5 + (h % 9) / 10) * 10) / 10;
    return { sv: sv, lv: lv, ld: ld, sal: sal, avgCompletion: avgCompletion };
  }

  /**
   * @param {string} monthKey
   * @param {object[]} dealerStores
   */
  function buildRegionSummaryRows(monthKey, dealerStores) {
    var scale = scaleFactor(monthKey);
    var rows = [];
    var vnMonth =
      vnRef && vnRef.months
        ? vnRef.months[monthKey] || vnRef.months[Object.keys(vnRef.months).sort().pop()]
        : null;
    if (vnMonth && vnMonth.regions) {
      for (var vi = 0; vi < vnMonth.regions.length; vi++) {
        var vr = vnMonth.regions[vi];
        var vm = mockRegionMetrics(vr.rg, vr.storeCount, monthKey, scale);
        rows.push({
          rg: vr.rg,
          storeCount: vr.storeCount,
          realRegion: true,
          realStores: true,
          storeNames: vr.storeNames || [],
          sv: vm.sv,
          lv: vm.lv,
          ld: vm.ld,
          sal: vm.sal,
          avgCompletion: vm.avgCompletion,
        });
      }
    }
    var byRg = {};
    (dealerStores || []).forEach(function (s) {
      if (s.region === '越南区' && s.dataSource === 'vietnam_reference') return;
      var rg = s.region || '其他';
      byRg[rg] = (byRg[rg] || 0) + 1;
    });
    var order = ['北区', '南区', '西区', '东区', '其他'];
    for (var oi = 0; oi < order.length; oi++) {
      var rgName = order[oi];
      if (!byRg[rgName] || rgName === '越南区') continue;
      var dm = mockRegionMetrics(rgName, byRg[rgName], monthKey, scale);
      rows.push({
        rg: rgName,
        storeCount: byRg[rgName],
        realRegion: true,
        realStores: true,
        sv: dm.sv,
        lv: dm.lv,
        ld: dm.ld,
        sal: dm.sal,
        avgCompletion: dm.avgCompletion,
      });
    }
    return rows;
  }

  function renderRegionSummaryTable(monthKey, dealerStores) {
    var rows = buildRegionSummaryRows(monthKey, dealerStores);
    if (!rows.length) {
      return { tbody: '', foot: '暂无区域汇总数据' };
    }
    var tb = '';
    for (var i = 0; i < rows.length; i++) {
      var r = rows[i];
      tb +=
        '<tr><td>' +
        r.rg +
        '</td><td class="num">' +
        r.storeCount +
        '</td><td class="num">' +
        r.sv +
        '</td><td class="num">' +
        r.lv +
        '</td><td class="num">' +
        r.ld +
        '</td><td class="num">' +
        fmtNum(r.sal) +
        '</td><td class="num">' +
        r.avgCompletion +
        '%</td></tr>';
    }
    var vnNames =
      rows[0] && rows[0].storeNames && rows[0].storeNames.length
        ? ' · 越南店：' + rows[0].storeNames.join('、')
        : '';
    var foot =
      '区域/门店数：越南区来自 Data collecet(5).xlsx（' +
      (vnRef && vnRef.sourceFile ? vnRef.sourceFile : 'vn_data_collect_reference.json') +
      '）；海外代理商大区来自当前数据包统计' +
      vnNames +
      ' · 短视频/直播/线索/真实销售/完成率均值为演示 mock。';
    return { tbody: tb, foot: foot };
  }

  function renderStack(agg) {
    var h = '';
    for (var i = 0; i < agg.length; i++) {
      var r = agg[i];
      var t = r.ld || 1;
      var hs = Math.max(8, Math.round((r.Ls / t) * 110));
      var hl = Math.max(8, Math.round((r.Ll / t) * 110));
      var ho = Math.max(8, 130 - hs - hl);
      h +=
        '<div class="oi-stack-one">' +
        '<div class="oi-stack-v" style="height:130px">' +
        '<div class="seg oi-seg-o" style="height:' +
        ho +
        'px">' +
        r.Lo +
        '</div>' +
        '<div class="seg oi-seg-l" style="height:' +
        hl +
        'px">' +
        r.Ll +
        '</div>' +
        '<div class="seg oi-seg-s" style="height:' +
        hs +
        'px">' +
        r.Ls +
        '</div></div>' +
        '<div class="oi-stack-sum">合计 ' +
        r.ld +
        ' 条</div>' +
        '<div class="oi-stack-rg">' +
        r.rg +
        '</div></div>';
    }
    return h;
  }

  /**
   * @param {string} url
   * @returns {Promise<void>}
   */
  /**
   * @param {string} [channelUrl]
   * @param {string} [vnUrl]
   * @returns {Promise<void>}
   */
  function init(channelUrl, vnUrl) {
    if (ref && vnRef) return Promise.resolve();
    if (loadPromise) return loadPromise;
    var chUrl = channelUrl || 'data/online_channel_reference.json';
    var vUrl = vnUrl || 'data/vn_data_collect_reference.json';
    function fetchJson(url, fallback) {
      return fetch(url)
        .then(function (res) {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          return res.json();
        })
        .catch(function () {
          return fallback;
        });
    }
    loadPromise = Promise.all([
      fetchJson(chUrl, { stores: [], okrByMonth: {}, estRatio: 4, regionOrder: [] }),
      fetchJson(vnUrl, { months: {}, stores: [] }),
    ]).then(function (pair) {
      ref = pair[0];
      vnRef = pair[1];
    });
    return loadPromise;
  }

  /**
   * @param {{ monthKey?: string, dealerStores?: object[] }} opts
   * @returns {string}
   */
  function renderHtml(opts) {
    opts = opts || {};
    var hasChannel = ref && ref.stores && ref.stores.length;
    var hasVn = vnRef && vnRef.months && Object.keys(vnRef.months).length;
    if (!hasChannel && !hasVn) {
      return (
        '<div class="glass-card oi-merged" id="oi-merged">' +
        '<div class="oi-head"><h2>线上经营 · 渠道与 OKR</h2>' +
        '<p>参考数据加载中或不可用，请刷新页面。</p></div></div>'
      );
    }
    var monthKey = opts.monthKey || '2026-05';
    if (!/^\d{4}-\d{2}$/.test(monthKey)) monthKey = '2026-05';
    var ml = hasChannel ? mainland(scaledStores(monthKey)) : [];
    var okr = hasChannel ? renderOkrTable(ml, monthKey) : { tbody: '', foot: '' };
    var agg = hasChannel ? aggRegions(ml) : [];
    var cust = customerOwnershipFromDealers(opts.dealerStores || []);
    var regionTbl = renderRegionSummaryTable(monthKey, opts.dealerStores || []);
    var channelBlock = hasChannel
      ? '<div class="oi-card">' +
        '<h3>真实销售 ÷ 经销商 OKR（当月目标）</h3>' +
        '<p class="oi-note">OKR 为当月销售目标（万元，不变）；<strong>真实销售</strong>为实际达成（万）；<strong>完成率</strong>= 真实销售 ÷ OKR；<strong>VERTU 介绍业绩</strong>为演示 mock；<strong>预估占比</strong> 固定 ' +
        ((ref && ref.estRatio) || 4) +
        '%；<strong>差异</strong>= 完成率 − 预估占比。</p>' +
        '<div class="oi-tbl-wrap"><table class="oi-grid oi-grid-wide"><thead><tr>' +
        '<th>区域</th><th>经销商·区域/门店</th><th class="num">OKR目标(万)</th><th class="num">真实销售(万)</th>' +
        '<th class="num">完成率%</th><th class="num">VERTU介绍业绩(万)</th><th class="num">VERTU占业绩%</th>' +
        '<th class="num">预估占比%</th><th class="num">与预估差异</th>' +
        '</tr></thead><tbody>' +
        okr.tbody +
        '</tbody></table></div>' +
        '<p class="oi-foot">' +
        okr.foot +
        '</p></div>' +
        '<div class="oi-two-col">' +
        '<div class="oi-card">' +
        '<h3>各渠道线索（条）</h3>' +
        '<div class="oi-bar-wrap">' +
        renderChannelBars(ml) +
        '</div></div>' +
        '<div class="oi-card">' +
        '<h3>客户来源（人）</h3>' +
        '<p class="oi-note">替代原「四周线索趋势」：代理商 <strong>自有有效客户</strong> 与 <strong>VERTU 推送</strong>（进店人数扣除自有有效口径）。</p>' +
        '<div class="oi-bar-wrap">' +
        renderCustomerBars(cust.own, cust.vertu) +
        '</div></div></div>' +
        '<div class="oi-card">' +
        '<h3>区域线索堆叠（条）</h3>' +
        '<div class="oi-stack-row">' +
        renderStack(agg) +
        '</div></div>'
      : '';
    return (
      '<div class="glass-card oi-merged p-0 overflow-hidden" id="oi-merged">' +
      '<div class="oi-head">' +
      '<h2>经销商线上经营 · 并入客流分析</h2>' +
      '<p>统计月 <strong>' +
      monthKey +
      '</strong> · 数据优先级：vertu CLI 业绩 → Excel 参考 JSON → mock。OKR/渠道为参考表；客户来源为当前代理商汇总。</p>' +
      '</div>' +
      '<div class="oi-dark oi-panel">' +
      channelBlock +
      '<div class="oi-card">' +
      '<h3>区域汇总表（经销商·越南登记门店）</h3>' +
      '<p class="oi-note"><strong>区域、门店数</strong>为真实（越南四店来自 Data collecet(5).xlsx；代理商大区来自当前页数据包）；<strong>短视频 / 直播 / 线索 / 真实销售 / 完成率均值</strong>为 mock。</p>' +
      '<div class="oi-tbl-wrap"><table class="oi-grid oi-grid-wide"><thead><tr>' +
      '<th>区域</th><th class="num">门店数</th><th class="num">短视频条数</th><th class="num">直播场次</th>' +
      '<th class="num">线索</th><th class="num">真实销售(万)</th><th class="num">完成率均值%</th>' +
      '</tr></thead><tbody>' +
      regionTbl.tbody +
      '</tbody></table></div>' +
      '<p class="oi-foot">' +
      regionTbl.foot +
      '</p></div>' +
      '</div></div>'
    );
  }

  global.WalkinOnlineMerged = {
    init: init,
    renderHtml: renderHtml,
    isReady: function () {
      return !!(ref && ref.stores && ref.stores.length);
    },
  };
})(typeof window !== 'undefined' ? window : globalThis);
