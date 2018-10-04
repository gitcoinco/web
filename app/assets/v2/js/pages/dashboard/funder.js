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
    registerPluginForNoData();
    var chart = updateChart(null);

    var $currentChartFilter = null;

    handleChartChange();

    function registerPluginForNoData() {
      // Display some default text if no data was found.
      Chart.plugins.register({
        afterDraw: function(chart) {
          var datasets = chart.data.datasets;

          if (datasets.length === 0 || datasets[0].data.length === 0) {
            // No data is present
            var ctx = chart.chart.ctx;
            var width = chart.chart.width;
            var height = chart.chart.height;

            chart.clear();
            ctx.save();
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = '#000000';
            ctx.font = '22px normal Muli sans-serif';
            ctx.fillText('No data to display.', width / 2, height / 2);
            ctx.restore();
          }
        }
      });
    }

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

      // When there is only 1 datapoint for a graph we'll pad the datapoint and label with null values
      // so the datapoint is nicely displayed in the middle of the chart.
      if (monthlyData.data.length === 1) {
        monthlyData.data = [ null, monthlyData.data[0], null ];
        monthlyData.labels = [ '', monthlyData.labels[0], '' ];
      }

      if (weeklyData.data.length === 1) {
        weeklyData.data = [ null, weeklyData.data[0], null ];
        weeklyData.labels = [ '', weeklyData.labels[0], '' ];
      }

      if (yearlyData.data.length === 1) {
        yearlyData.data = [ null, yearlyData.data[0], null ];
        yearlyData.labels = [ '', yearlyData.labels[0], '' ];
      }

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
        },
        maintainAspectRatio: false
      };

      var context2d = document.getElementById('funder-dashboard__payout-history__chart').getContext('2d');

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
        submitTotalBudget();
      }
    });

    $('.funder-dashboard__stats__stat--total-budget__budget-input__submit').click(function() {
      submitTotalBudget();
    });

    function submitTotalBudget() {
      var isMonthly = $('.control--total-budget--monthly').hasClass('control--selected');
      var isQuarterly = $('.control--total-budget--quarterly').hasClass('control--selected');

      var updateData = {
        isMonthly: isMonthly,
        isQuarterly: isQuarterly,
        budget: $totalBudget.val()
      };

      if (updateData.budget === '') {
        alert('Budget cannot be empty');
        return;
      }

      $.ajax({
        url: '/update_funder_total_budget',
        method: 'POST',
        data: JSON.stringify(updateData),
        dataType: 'json'
      }).done(function() {
        setUpdatedTotalCookie('fd_total_last_updated', 1);
        location.reload();
      });
    }

    // Monthly / Quarterly
    var $totalBudgetControls = $('.control--total-budget');

    $totalBudgetControls.click(function() {
      $totalBudgetControls.removeClass('control--selected');
      $(this).addClass('control--selected');
    });

    // used to force a refresh of the view, so that users see their new total budget once
    // they type in one
    function setUpdatedTotalCookie(name, days) {
      var date = new Date();
      var expires = '; expires=' + date.toUTCString();
      var value = date.toUTCString();

      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      document.cookie = name + '=' + value + expires + '; path=/';
    }
  }

  // used both by bounties and outgoing funds
  // any object the resulting fns are to be used on must have the created_on and worthDollars properties
  function getSortFn(sortFilterVal) {
    switch (sortFilterVal) {
      case 'Recent':
        return function(fund1, fund2) {
          return dateComparison(fund1.createdOn, fund2.createdOn);
        };
      case 'Oldest':
        return function(fund1, fund2) {
          return -dateComparison(fund1.createdOn, fund2.createdOn);
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
    if (outgoingFunds.length === 0) {
      // hiding this module server-side in the html.
      return;
    }

    var $container = $('.funder-dashboard__outgoing-funds__funds');
    var $fundTemplate = $('.funder-dashboard__outgoing-funds__funds__fund--template');

    var fundBaseSel = 'funder-dashboard__outgoing-funds__funds__fund';
    var cbRenderFunds = renderOutgoingFunds.bind(this, $container, $fundTemplate, fundBaseSel);

    var getFunds = getOutgoingFunds.bind(this, outgoingFunds, cbRenderFunds);

    changePageRelative(outgoingFunds, 0);
    $('.funder-dashboard__outgoing-funds__filter').change(function() {
      changePageAbsolute(1);
    });

    activateOrRemovePaginationControls();

    function activateOrRemovePaginationControls() {
      if (outgoingFunds.length > 5) {
        $('.funder-dashboard__outgoing-funds__pagination__prev').click(function() {
          changePageRelative(outgoingFunds, -1);
        });

        $('.funder-dashboard__outgoing-funds__pagination__next').click(function() {
          changePageRelative(outgoingFunds, 1);
        });
      } else {
        $('.funder-dashboard__outgoing-funds__pagination').remove();
      }
    }

    function clearFunds() {
      $container.find(classSel(fundBaseSel + ':not(' + classSel(fundBaseSel) + '--template)')).remove();
    }

    function renderOutgoingFunds($container, $fundTemplate, fundBaseSel, funds) {
      var $nothingWasFoundText = $('.funder-dashboard__outgoing-funds__nothing-was-found');
      var $fundsTable = $('.funder-dashboard__outgoing-funds__funds-wrapper');

      if (funds.length === 0) {
        $nothingWasFoundText.removeClass('d-none');
        $fundsTable.addClass('d-none');
        return;
      }

      $nothingWasFoundText.addClass('d-none');
      $fundsTable.removeClass('d-none');

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

      var page = Number($('.funder-dashboard__outgoing-funds__pagination__page').html());
      var PAGE_SIZE = 5;

      filteredFunds = filteredFunds.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

      cbRenderFunds(filteredFunds);

      function getTypeOrStatusFilter(filterBaseSel) {
        return $(classSel(filterBaseSel) + '--type-or-status').find(':selected');
      }

      function getSortByFilter(filterBaseSel) {
        return $(classSel(filterBaseSel) + '--age-or-value').find(':selected');
      }
    }

    function changePageRelative(allFunds, increment) {
      function adjustPaginationControlsDisplayed(currPage, maxPage, minPage) {
        var $prev = $('.funder-dashboard__outgoing-funds__pagination__prev');
        var $next = $('.funder-dashboard__outgoing-funds__pagination__next');

        if (currPage === minPage) {
          $prev.addClass('invisible');
        } else {
          $prev.removeClass('invisible');
        }

        if (currPage === maxPage) {
          $next.addClass('invisible');
        } else {
          $next.removeClass('invisible');
        }
      }
      var PAGE_SIZE = 5;
      var outgoingFundsCount = allFunds.length;
      var maxPage = Math.floor(outgoingFundsCount / PAGE_SIZE) + 1;
      var minPage = 1;

      var $page = $('.funder-dashboard__outgoing-funds__pagination__page');
      var oldPage = Number($page.html());
      var newPage = oldPage + increment;

      if (newPage > maxPage) {
        newPage = minPage;
      }

      if (newPage < minPage) {
        newPage = maxPage;
      }

      $page.html(newPage);
      adjustPaginationControlsDisplayed(newPage, maxPage, minPage);

      clearFunds();
      getFunds();
    }

    function changePageAbsolute(newPage) {
      var $page = $('.funder-dashboard__outgoing-funds__pagination__page');

      $page.html(newPage);
      clearFunds();
      getFunds();
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

    changePageRelative(bounties, 0);
    $('.funder-dashboard__all-bounties__filter').change(function() {
      changePageAbsolute(1);
    });

    activateOrRemovePaginationControls();

    function activateOrRemovePaginationControls() {
      if (bounties.length > 5) {
        $('.funder-dashboard__all-bounties__pagination__prev').click(function() {
          changePageRelative(bounties, -1);
        });

        $('.funder-dashboard__all-bounties__pagination__next').click(function() {
          changePageRelative(bounties, 1);
        });
      } else {
        $('.funder-dashboard__all-bounties__pagination').remove();
      }
    }

    function changePageRelative(allBounties, increment) {
      function adjustPaginationControlsDisplayed(currPage, maxPage, minPage) {
        var $prev = $('.funder-dashboard__all-bounties__pagination__prev');
        var $next = $('.funder-dashboard__all-bounties__pagination__next');

        if (currPage === minPage) {
          $prev.addClass('invisible');
        } else {
          $prev.removeClass('invisible');
        }

        if (currPage === maxPage) {
          $next.addClass('invisible');
        } else {
          $next.removeClass('invisible');
        }
      }

      var PAGE_SIZE = 5;
      var bountiesCount = bounties.length;
      var max_page = Math.floor(bountiesCount / PAGE_SIZE) + 1;
      var min_page = 1;

      var $page = $('.funder-dashboard__all-bounties__pagination__page');
      var oldPage = Number($page.html());
      var newPage = oldPage + increment;

      if (newPage > max_page) {
        newPage = min_page;
      }

      if (newPage < min_page) {
        newPage = max_page;
      }

      $page.html(newPage);
      adjustPaginationControlsDisplayed(newPage, max_page, min_page);

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
      var $nothingWasFoundText = $('.funder-dashboard__all-bounties__nothing-was-found');
      var $bountiesTable = $('.funder-dashboard__all-bounties__bounties-wrapper');

      if (bounties.length === 0) {
        $nothingWasFoundText.removeClass('d-none');
        $bountiesTable.addClass('d-none');
        return;
      }

      $nothingWasFoundText.addClass('d-none');
      $bountiesTable.removeClass('d-none');

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

      var sortFn = getSortFn($sortFilter.val());

      filteredBounties = filteredBounties.sort(function(fund1, fund2) {
        return sortFn(fund1, fund2);
      });

      var page = Number($('.funder-dashboard__all-bounties__pagination__page').html());
      var PAGE_SIZE = 5;

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
    var baseClassName = 'issue-explorer-link';
    var $links = $('.' + baseClassName);

    $links.click(function(e) {
      e.preventDefault();
      var $this = $(this);
      var urlExplorer = $this.attr('href');

      if ($this.hasClass(baseClassName + '--bounties--active')) {
        urlExplorer = createdByMe(urlExplorer);
        urlExplorer = addQueryString('idx_status', 'open', urlExplorer);
      } else if ($this.hasClass(baseClassName + '--bounties--completed')) {
        urlExplorer = createdByMe(urlExplorer);
        urlExplorer = addQueryString('idx_status', 'done', urlExplorer);
      } else if ($this.hasClass(baseClassName + '--bounties--expired')) {
        urlExplorer = createdByMe(urlExplorer);
        urlExplorer = addQueryString('idx_status', 'expired', urlExplorer);
      } else if ($this.hasClass(baseClassName + '--contributors-comments')) {
        urlExplorer = createdByMe(urlExplorer);
        urlExplorer = addQueryString('idx_status', 'open', urlExplorer);
      } else if ($this.hasClass(baseClassName + '--payments--all')) {
        urlExplorer = createdByMe(urlExplorer);
      } else if ($this.hasClass(baseClassName + '--bounties--all')) {
        urlExplorer = createdByMe(urlExplorer);
      }

      function addQueryString(key, value, url) {
        if (urlExplorer.indexOf('?') < 0) {
          url += '?' + key + '=' + value;
        } else {
          url += '&' + key + '=' + value;
        }

        return url;
      }

      function createdByMe(url) {
        return addQueryString('bounty_filter', 'createdByMe', url);
      }

      window.open(urlExplorer, '_blank').opener = null;
    });
  }

  function activateTaxYearCsvExport() {
    $('.funder-dashboard__tax-reporting__bounties__download-report').click(function() {
      utils.download(window.taxReportCsv, 'GitcoinPaidBountiesThisYear.csv', 'text/csv;encoding:utf-8');
    });
  }

  activatePayoutHistory();
  activateTotalBudget();
  activateLinksToIssueExplorer();
  activateTaxYearCsvExport();

  var outgoingFunds = window.outgoingFunds.items;
  var funderBounties = window.allBounties.items;

  activateOutgoingFunds(outgoingFunds);
  activateAllBounties(funderBounties);
});
