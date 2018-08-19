$(function() {
  var utils = {
    stringCompareIgnoreCase: function(str1, str2) {
      if (!str1 || !str2) {
        return false;
      }

      if (str1.toUpperCase && str2.toUpperCase) {
        return str1.toUpperCase() === str2.toUpperCase();
      }

      return (str1 === str2);
    },

    updateBemElementInParent: function($parent, classSelectorBase, elementName, elementValue) {
      var $element = $parent.find(classSel(classSelectorBase) + '__' + elementName);

      update($element, elementValue);

      function update($el, htmlContent) {
        $el.html(htmlContent);
      }
    },

    download: function(content, fileName, mimeType) {
      // Won't work in IE <= 9
      var a = document.createElement('a');

      mimeType = mimeType || 'application/octet-stream';

      if (navigator.msSaveBlob) { // IE10
        navigator.msSaveBlob(new Blob([content], {
          type: mimeType
        }), fileName);
      } else if (URL && 'download' in a) {
        a.href = URL.createObjectURL(new Blob([content], {
          type: mimeType
        }));
        a.setAttribute('download', fileName);
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      } else {
        location.href = 'data:application/octet-stream,' + encodeURIComponent(content);
      }
    }
  };

  function activatePayoutHistory() {
    var chart = updateChart(null);

    var $currentChartFilter = null;

    handleChartChange();

    function handleChartChange() {
      $('.funder-dashboard__payout-history__control').click(function() {
        if ($(this) !== $currentChartFilter) {
          var classSelected = 'funder-dashboard__payout-history__control--selected';

          $('.funder-dashboard__payout-history__control').removeClass(classSelected);
          $currentChartFilter = $(this);
          $currentChartFilter.addClass(classSelected);
          chart = updateChart(chart);
        }
      });
    }

    function updateChart(oldChart) {
      if (oldChart) {
        oldChart.clear();
      }
      return renderChart();
    }

    function renderChart() {
      var chartSettings = getChartSettings();

      return new Chart(chartSettings.context2d, {
        data: chartSettings.data,
        options: chartSettings.options,
        type: 'line'
      });
    }

    function getChartSettings() {
      var monthlyData = window.funderDashboardPayoutChartData.monthlyData;
      var weeklyData = window.funderDashboardPayoutChartData.weeklyData;
      var yearlyData = window.funderDashboardPayoutChartData.yearlyData;

      var filterBaseSel = 'funder-dashboard__payout-history__control';

      var $selected = $(classSel(filterBaseSel) + '--selected');
      var isWeekly = $selected.hasClass(filterBaseSel + '--weekly');
      var isMonthly = $selected.hasClass(filterBaseSel + '--monthly');
      var isYearly = $selected.hasClass(filterBaseSel + '--yearly');

      var plotData = null;
      var labels = null;

      if (isWeekly) {
        plotData = weeklyData.data;
        labels = weeklyData.labels;
      } else if (isMonthly) {
        plotData = monthlyData.data;
        labels = monthlyData.labels;
      } else if (isYearly) {
        plotData = yearlyData.data;
        labels = yearlyData.labels;
      }

      var data = {
        datasets: [{
          data: plotData,
          borderColor: '#3e00ff',
          backgroundColor: '#eff7fd',
          lineTension: 0,
          fillColor: '#eff7fd'
        }],
        labels: labels
      };

      var options = {
        scales: {
          yAxes: [
            {
              ticks: {
                callback: function(value, index, labels) {
                  return '$' + value;
                }
              }
            }
          ]
        },
        legend: {
          display: false
        }
      };

      var context2d = document.getElementById('funder-dashhboard__payout-history__chart').getContext('2d');

      return {
        data: data,
        options: options,
        context2d: context2d
      };
    }
  }

  function activateTotalBudget() {
    var $totalBudget = $('.funder-dashboard__stats__stat--total-budget__budget-input');

    $totalBudget.keypress(function(e) {
      if (e.key == 'Enter') {
        console.log('User inputted total budget: \r\n' + this.value);

        var isMonthly = $('.control--total-budget--monthly').hasClass('control--selected');
        var isQuarterly = $('.control--total-budget--quarterly').hasClass('control--selected');

        console.log('Is monthly total budget: ' + isMonthly);
        console.log('Is quarterly total budget: ' + isQuarterly);

        alert('We\'re sorry, but this feature is not currently available');
      }
    });

    // Monthly / Quarterly
    var $totalBudgetControls = $('.control--total-budget');

    $totalBudgetControls.click(function() {
      $totalBudgetControls.removeClass('control--selected');
      $(this).addClass('control--selected');
    });
  }

  // used both by bounties and outgoing funds
  // any object the resulting fns are to be used on must have the created_on and worthDollars properties
  function getSortFn(sortFilterVal) {
    switch (sortFilterVal) {
      case 'Recent':
        return function(fund1, fund2) {
          return dateComparison(fund1.created_on, fund2.created_on);
        };
      case 'Oldest':
        return function(fund1, fund2) {
          return -dateComparison(fund1.created_on, fund2.created_on);
        };
      case 'Highest Value':
        return function(fund1, fund2) {
          return -(parseFloat(fund1.worthDollars) - parseFloat(fund2.worthDollars));
        };
      case 'Lowest Value':
        return function(fund1, fund2) {
          return parseFloat(fund1.worthDollars) - parseFloat(fund2.worthDollars);
        };
      default:
        return function() {
          return 0;
        };
    }
  }

  // TODO: date1 and date2 are datetime objects coming from the api. Need a way to compare them
  function dateComparison(date1, date2) {
    if (date1 < date2) {
      return -1;
    }

    if (date1 > date2) {
      return 1;
    }

    return 0;
  }

  function activateOutgoingFunds(outgoingFunds) {
    var $container = $('.funder-dashboard__outgoing-funds__funds');
    var $fundTemplate = $('.funder-dashboard__outgoing-funds__funds__fund--template');

    var fundBaseSel = 'funder-dashboard__outgoing-funds__funds__fund';
    var cbRenderFunds = renderOutgoingFunds.bind(this, $container, $fundTemplate, fundBaseSel);

    var getFunds = getOutgoingFunds.bind(this, outgoingFunds, cbRenderFunds);

    getFunds();
    $('.funder-dashboard__outgoing-funds__filter').change(function() {
      clearFunds();
      getFunds();
    });

    function clearFunds() {
      $container.find(classSel(fundBaseSel + ':not(' + classSel(fundBaseSel) + '--template)')).remove();
    }

    function renderOutgoingFunds($container, $fundTemplate, fundBaseSel, funds) {
      for (var i = 0; i < funds.length; ++i) {
        var fund = funds[i];

        var $clone = $fundTemplate.clone();

        utils.updateBemElementInParent($clone, fundBaseSel, 'id', fund.id);
        utils.updateBemElementInParent($clone, fundBaseSel, 'title', fund.title);
        utils.updateBemElementInParent($clone, fundBaseSel, 'type', fund.type);
        utils.updateBemElementInParent($clone, fundBaseSel, 'status', fund.status);
        var $etherscanLink = $clone.find(classSel(fundBaseSel) + '__view-etherscan');
        
        if (fund.etherscanLink) {
          $etherscanLink.attr('href', fund.etherscanLink);
        } else {
          $clone.find(classSel(fundBaseSel) + '__etherscan-link-placeholder').removeClass('d-none');
          $etherscanLink.addClass('d-none');
        }
        utils.updateBemElementInParent($clone, fundBaseSel, 'worth__dollars', fund.worthDollars);
        utils.updateBemElementInParent($clone, fundBaseSel, 'worth__eth', fund.worthEth);

        if (fund.status === 'Pending') {
          $clone.addClass(fundBaseSel + '--pending');
        }

        $clone.removeClass(fundBaseSel + '--template');
        $container.append($clone);
      }
    }

    function getOutgoingFunds(funds, cbRenderFunds) {
      var filterBaseSel = 'funder-dashboard__outgoing-funds__filter';

      var $typeStatusFilter = getTypeOrStatusFilter(filterBaseSel);
      var $sortFilter = getSortByFilter(filterBaseSel);

      var filteredFunds = funds.filter(function(fund) {
        if ($typeStatusFilter.data('is-all-filter')) {
          return true;
        }

        if ($typeStatusFilter.data('is-type-filter')) {
          return utils.stringCompareIgnoreCase(fund.type, $typeStatusFilter.val());
        } else if ($typeStatusFilter.data('is-status-filter')) {
          return utils.stringCompareIgnoreCase(fund.status, $typeStatusFilter.val());
        }
      });

      var sortFn = getSortFn($sortFilter.val());

      filteredFunds = filteredFunds.sort(function(fund1, fund2) {
        return sortFn(fund1, fund2);
      });

      cbRenderFunds(filteredFunds);

      function getTypeOrStatusFilter(filterBaseSel) {
        return $(classSel(filterBaseSel) + '--type-or-status').find(':selected');
      }

      function getSortByFilter(filterBaseSel) {
        return $(classSel(filterBaseSel) + '--age-or-value').find(':selected');
      }
    }
  }

  function classSel(className) {
    return '.' + className;
  }

  function activateAllBounties(bounties) {
    var $container = $('.funder-dashboard__all-bounties__bounties');
    var $bountyTemplate = $('.funder-dashboard__all-bounties__bounties__bounty--template');

    var bountyBaseSel = 'funder-dashboard__all-bounties__bounties__bounty';
    var cbRenderBounties = renderBounties.bind(this, $container, $bountyTemplate, bountyBaseSel);
    var boundGetBounties = getBounties.bind(this, bounties, cbRenderBounties);

    boundGetBounties();
    $('.funder-dashboard__all-bounties__filter').change(function() {
      changePageAbsolute(1);
      clearBounties();
      boundGetBounties();
    });

    $('.funder-dashboard__all-bounties__pagination__prev').click(function() {
      changePageRelative(bounties, -1);
    });

    $('.funder-dashboard__all-bounties__pagination__next').click(function() {
      changePageRelative(bounties, 1);
    });

    function changePageRelative(allBounties, increment) {
      var PAGE_SIZE = 5;
      var bountiesCount = bounties.length;
      var page_number_max = Math.floor(bountiesCount / PAGE_SIZE) + 1;
      var page_number_min = 1;

      var $page = $('.funder-dashboard__all-bounties__pagination__page');
      var oldPage = Number($page.html());
      var newPage = oldPage + increment;

      if (newPage > page_number_max) {
        newPage = page_number_max;
      }

      if (newPage < page_number_min) {
        newPage = page_number_max;
      }

      $page.html(newPage);

      clearBounties();
      boundGetBounties();
    }

    function changePageAbsolute(newPage) {
      var $page = $('.funder-dashboard__all-bounties__pagination__page');

      $page.html(newPage);
      clearBounties();
      boundGetBounties();
    }

    function clearBounties() {
      $container.find(classSel(bountyBaseSel + ':not(' + classSel(bountyBaseSel) + '--template)')).remove();
    }

    function renderBounties($container, $bountyTemplate, bountyBaseSel, bounties) {
      for (var i = 0; i < bounties.length; ++i) {
        var $clone = $bountyTemplate.clone();
        var bounty = bounties[i];

        utils.updateBemElementInParent($clone, bountyBaseSel, 'id', bounty.id);
        utils.updateBemElementInParent($clone, bountyBaseSel, 'title', bounty.title);
        utils.updateBemElementInParent($clone, bountyBaseSel, 'type', bounty.type);
        utils.updateBemElementInParent($clone, bountyBaseSel, 'status', bounty.status);
        $clone.find(classSel(bountyBaseSel) + '__view-github').attr('href', bounty.githubLink);
        utils.updateBemElementInParent($clone, bountyBaseSel, 'worth__dollars', bounty.worthDollars);
        utils.updateBemElementInParent($clone, bountyBaseSel, 'worth__eth', bounty.worthEth);

        if (bounty.status === 'started') {
          $clone.addClass(bountyBaseSel + '--started');
        } else if (bounty.status === 'stopped') {
          $clone.addClass(bountyBaseSel + '--stopped');
        } else if (bounty.status === 'submitted') {
          $clone.addClass(bountyBaseSel + '--submitted');
        } else if (bounty.status === 'open') {
          $clone.addClass(bountyBaseSel + '--open');
        }

        $clone.removeClass(bountyBaseSel + '--template');
        $container.append($clone);
      }
    }

    function getBounties(bounties, cbRenderBounties) {
      var filterBaseSel = 'funder-dashboard__all-bounties__filter';

      var $typeStatusFilter = getTypeOrStatusFilter(filterBaseSel);
      var $sortFilter = getSortByFilter(filterBaseSel);


      var filteredBounties = bounties.filter(function(bounty) {
        if ($typeStatusFilter.data('is-all-filter')) {
          return true;
        }

        if ($typeStatusFilter.data('is-status-pending-or-claimed-filter')) {
          // 'Pending' || 'Claimed'
          return utils.stringCompareIgnoreCase(bounty.statusPendingOrClaimed, $typeStatusFilter.val());
        }
      });

      var page = Number($('.funder-dashboard__all-bounties__pagination__page').html());
      var PAGE_SIZE = 5;

      var sortFn = getSortFn($sortFilter.val());

      filteredBounties = filteredBounties.sort(function(fund1, fund2) {
        return sortFn(fund1, fund2);
      });

      filteredBounties = filteredBounties.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

      cbRenderBounties(filteredBounties);

      function getTypeOrStatusFilter(filterBaseSel) {
        return $(classSel(filterBaseSel) + '--type-or-status').find(':selected');
      }

      function getSortByFilter(filterBaseSel) {
        return $(classSel(filterBaseSel) + '--age-or-value').find(':selected');
      }
    }
  }

  function activateLinksToIssueExplorer() {
    var localStorage;

    try {
      localStorage = window.localStorage;
    } catch (e) {
      // Won't throw an error when doing things with localStorage, but will be useless when redirecting to issueExplorer.
      // Not a big issue, but funders with no localStorage support will just get redirected to the explorer
      // without applied filters
      localStorage = {};
    }

    var baseLinkSel = 'issue-explorer-link';
    var $links = $('.' + baseLinkSel);

    $links.click(function(e) {
      e.preventDefault();
      var $this = $(this);
      var href = $this.attr('href');

      resetFilters();

      if ($this.hasClass(baseLinkSel + '--bounties--expiring')) {
        addToLocalStorage('bounty_owner_github_username', document.contxt.github_handle);
        addToLocalStorage('idx_status', 'open');
        addToLocalStorage('order_by', 'web3_created');
      } else if ($this.hasClass(baseLinkSel + '--bounties--active')) {
        addToLocalStorage('bounty_owner_github_username', document.contxt.github_handle);
        addToLocalStorage('idx_status', 'open');
      } else if ($this.hasClass(baseLinkSel + '--bounties--completed')) {
        addToLocalStorage('bounty_owner_github_username', document.contxt.github_handle);
        addToLocalStorage('idx_status', 'done');
      } else if ($this.hasClass(baseLinkSel + '--bounties--expired')) {
        addToLocalStorage('bounty_owner_github_username', document.contxt.github_handle);
        addToLocalStorage('idx_status', 'expired');
      } else if ($this.hasClass(baseLinkSel + '--contributors-comments')) {
        addToLocalStorage('bounty_owner_github_username', document.contxt.github_handle);
        // TODO: How do I get the issues with new comments? Or is it fine to just redirect to open issues?
        addToLocalStorage('idx_status', 'open');
      } else if ($this.hasClass(baseLinkSel + '--payments--all')) {
        addToLocalStorage('bounty_owner_github_username', document.contxt.github_handle);
        // TODO: I need something similar to status_in. Also, is "paid" the same as "done"?
      } else if ($this.hasClass(baseLinkSel + '--bounties--all')) {
        addToLocalStorage('bounty_owner_github_username', document.contxt.github_handle);
      }

      function addToLocalStorage(key, value) {
        localStorage[key] = value;
      }

      window.location.href = href;
    });

    var sidebar_keys = [
      'experience_level',
      'project_length',
      'bounty_type',
      'bounty_filter',
      'network',
      'idx_status',
      'tech_stack',
      'project_type',
      'permission_type'
    ];

    var resetFilters = function() {
      for (var i = 0; i < sidebar_keys.length; i++) {
        var key = sidebar_keys[i];

        localStorage[key] = null;
      }

      localStorage['bounty_owner_github_username'] = null;

      if (localStorage['keywords']) {
        localStorage['keywords'].split(',').forEach(function(v, k) {
          localStorage['keywords'] = localStorage['keywords'].replace(v, '').replace(',,', ',');
          // Removing the start and last comma to avoid empty element when splitting with comma
          localStorage['keywords'] = localStorage['keywords'].replace(/^,|,\s*$/g, '');
        });
      }
    };
  }

  function activateTaxYearCsvExport() {
    $('.funder-dashboard__tax-reporting__bounties__download-report').click(function() {
      var csvRows = window.taxReportCsv;

      var csvContent = '';

      csvRows.forEach(function(infoArray, index) {
        var dataString = infoArray.join(',');

        csvContent += index < csvRows.length ? dataString + '\r\n' : dataString;
      });

      utils.download(csvContent, 'GitcoinPaidBountiesThisYear.csv', 'text/csv;encoding:utf-8');
    });
  }

  activatePayoutHistory();
  activateTotalBudget();
  activateLinksToIssueExplorer();
  activateTaxYearCsvExport();

  var outgoingFunds = window.outgoingFunds.items;
  var funderBounties = window.allBounties.items;

  activateOutgoingFunds(outgoingFunds.slice(0, 5));
  activateAllBounties(funderBounties);
});

