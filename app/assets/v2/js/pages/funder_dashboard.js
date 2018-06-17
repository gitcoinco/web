$(function () {
  function activateChart() {
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
      // TODO: Get these from the server
      var monthlyData = {
        data: [80, 305, 50, 105, 405, 150, 200, 300],
        labels: ["January", "February", "March", "April", "May", "June", "July", "August"]
      };

      var weeklyData = {
        data: [50, 105, 405, 150, 200, 300, 80, 305],
        labels: [1, 2, 3, 4, 5, 6, 7, 8]
      };

      var yearlyData = {
        data: [50000, 70000, 90000, 30000],
        labels: [2016, 2017, 2018, 30000]
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
          fillColor: '#eff7fd',
        }],
        labels: labels,
      };

      var options = {
        scales: {
          yAxes: [
            {
              ticks: {
                callback: function (value, index, labels) {
                  return '$' + value;
                }
              },
            }
          ],
        },
        legend: {
          display: false
        }
      };

      var context2d = document.getElementById("funder-dashhboard__payout-history__chart").getContext("2d");

      return {
        data: data,
        options: options,
        context2d: context2d
      }
    }
  };

  function activateTotalBudget() {
    var $totalBudget = $('.funder-dashboard__stats__stat--total-budget').find('.funder-dashboard__stats__stat__footer');
  };

  function activateOutgoingFunds() {
    var $container = $('.funder-dashboard__outgoing-funds__funds');
    var $fundTemplate = $('.funder-dashboard__outgoing-funds__funds__fund--template');

    var fundBaseSel = 'funder-dashboard__outgoing-funds__funds__fund';
    var cbRenderFunds = renderOutgoingFunds.bind(this, $container, $fundTemplate, fundBaseSel);
    var getFunds = getOutgoingFunds.bind(this, cbRenderFunds);

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
        var $clone = $fundTemplate.clone();
        var fund = funds[i];

        updateBemElementInParent($clone, fundBaseSel, 'id', fund.id);
        updateBemElementInParent($clone, fundBaseSel, 'title', fund.title);
        updateBemElementInParent($clone, fundBaseSel, 'type', fund.type);
        updateBemElementInParent($clone, fundBaseSel, 'status', fund.status);
        $clone.find(classSel(fundBaseSel) + '__view-etherscan').attr('href', fund.etherscanLink);
        updateBemElementInParent($clone, fundBaseSel, 'worth__dollars', fund.worthDollars);
        updateBemElementInParent($clone, fundBaseSel, 'worth__eth', fund.worthEth);

        if (fund.status === 'Pending') {
          $clone.addClass(fundBaseSel + '--pending')
        }

        $clone.removeClass(fundBaseSel + '--template');
        $container.append($clone);
      }
    }

    function getOutgoingFunds(cbRenderFunds) {
      var filterBaseSel = 'funder-dashboard__outgoing-funds__filter';

      // below should be an endpoint call, these 2 should be query params: typeOrStatus and ageOrValue
      var includeOnly = getTypeOrStatusFilterValue(filterBaseSel);
      var orderBy = getAgeOrValueFilterValue(filterBaseSel);

      var postUrl = window.funderDashboardUrls.outgoingFundsUrl + "?includeOnly=" + includeOnly + "&orderBy=" + orderBy;

      $.post(postUrl, function(data) {
        var funds = $.parseJSON(data.funds);
        cbRenderFunds(funds);
      });

      function getTypeOrStatusFilterValue(filterBaseSel) {
        return $(classSel(filterBaseSel) + '--type-or-status').find(':selected').val();
      }

      function getAgeOrValueFilterValue(filterBaseSel) {
        return $(classSel(filterBaseSel) + '--age-or-value').find(':selected').val();
      }
    }
  }

  function updateBemElementInParent($parent, classSelectorBase, elementName, elementValue) {
    var $element = $parent.find(classSel(classSelectorBase) + '__' + elementName);
    update($element, elementValue);

    function update($el, htmlContent) {
      $el.html(htmlContent);
    }
  }

  function classSel(className) {
    return '.' + className;
  }

  function activateAllBounties() {
    var $container = $('.funder-dashboard__all-bounties__bounties');
    var $bountyTemplate = $('.funder-dashboard__all-bounties__bounties__bounty--template');

    var bountyBaseSel = 'funder-dashboard__all-bounties__bounties__bounty';
    var cbRenderBounties = renderOutgoingFunds.bind(this, $container, $bountyTemplate, bountyBaseSel);
    var getBounties = getAllBounties.bind(this, cbRenderBounties);

    getBounties();
    $('.funder-dashboard__all-bounties__filter').change(function() {
      clearBounties();
      getBounties();
    });

    function clearBounties() {
      $container.find(classSel(bountyBaseSel + ':not(' + classSel(bountyBaseSel) + '--template)')).remove();
    }

    function renderOutgoingFunds($container, $bountyTemplate, bountyBaseSel, bounties) {
      for (var i = 0; i < bounties.length; ++i) {
        var $clone = $bountyTemplate.clone();
        var bounty = bounties[i];

        updateBemElementInParent($clone, bountyBaseSel, 'id', bounty.id);
        updateBemElementInParent($clone, bountyBaseSel, 'title', bounty.title);
        updateBemElementInParent($clone, bountyBaseSel, 'type', bounty.type);
        updateBemElementInParent($clone, bountyBaseSel, 'status', bounty.status);
        $clone.find(classSel(bountyBaseSel) + '__view-github').attr('href', bounty.githubLink);
        updateBemElementInParent($clone, bountyBaseSel, 'worth__dollars', bounty.worthDollars);
        updateBemElementInParent($clone, bountyBaseSel, 'worth__eth', bounty.worthEth);

        if (bounty.status === 'Started') {
          $clone.addClass(bountyBaseSel + '--started');
        }
        else if (bounty.status === 'Stopped') {
          $clone.addClass(bountyBaseSel + '--stopped');
        }
        else if (bounty.status === 'Submitted') {
          $clone.addClass(bountyBaseSel + '--submitted');
        }

        $clone.removeClass(bountyBaseSel + '--template');
        $container.append($clone);
      }
    }

    function getAllBounties(cbRenderBounties) {
      var filterBaseSel = 'funder-dashboard__all-bounties__filter';

      var includeOnly = getTypeOrStatusFilterValue(filterBaseSel);
      var orderBy = getAgeOrValueFilterValue(filterBaseSel);

      var postUrl = window.funderDashboardUrls.bountiesUrl + "?includeOnly=" + includeOnly + "&orderBy=" + orderBy;

      $.post(postUrl, function(data) {
        var bounties = $.parseJSON(data.bounties);
        cbRenderBounties(bounties);
      });

      function getTypeOrStatusFilterValue(filterBaseSel) {
        return $(classSel(filterBaseSel) + '--type-or-status').find(':selected').val();
      }

      function getAgeOrValueFilterValue(filterBaseSel) {
        return $(classSel(filterBaseSel) + '--age-or-value').find(':selected').val();
      }
    }
  }

  activateChart();
  activateTotalBudget();
  activateOutgoingFunds();
  activateAllBounties();
});
