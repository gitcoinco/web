(function() {

  var dragit = window.dragit || {};

  window.dragit = dragit;

  dragit.version = '0.1.5';

  var vars = {
    'dev': false,
    evt: [],
    tc: [],
    list_closest_datapoint: [],
    svgLine: null,
    container: null,
    accessor_x: function(d) {
      return d[0];
    },
    accessor_y: function(d) {
      return d[1];
    },
    custom_focus: 'default',
    custom_trajectory: 'default',
    playback: {el: null}
  };

  dragit.custom = {};
  dragit.trajectory = {};
  dragit.statemachine = {};
  dragit.utils = {};
  dragit.evt = {};
  dragit.mouse = {};
  dragit.time = {};
  dragit.object = {};
  dragit.data = [];
  dragit.constraint = [];
  dragit.playback = {};

  dragit.statemachine = {current_state: 'idle', current_id: -1};

  dragit.time = {min: 0, max: 0, current: 0, step: 1, previous: 0, offset: 0};
  dragit.mouse = {scope: 'focus'};
  dragit.object = {update: function() {}, offsetX: 0, offsetY: 0, dragging: 'absolute'};
  dragit.evt = {register: function() {}, call: function() {}};

  dragit.custom.line = {
    'default': {'mark': 'svg:path', 'style': {'stroke': 'black', 'stroke-width': 2}, 'interpolate': 'linear'},
    'monotone': {'mark': 'svg:path', 'style': {'stroke': 'black', 'stroke-width': 2}, 'interpolate': 'monotone'}
  };

  dragit.custom.point = {
    'default': {'mark': 'svg:circle', 'style': {'stroke': 'black', 'stroke-width': 2},
      'attr': {'cx': vars.accessor_x, 'cy': vars.accessor_y, 'r': 3},
      'attr_static': {'cx': -10, 'cy': -10, 'r': 3}
    }
  };

  dragit.playback = {playing: false, loop: false, interpolation: 'none', speed: 1000};

  vars.svgLine = d3.svg.line()
    .x(vars.accessor_x)
    .y(vars.accessor_y)
    .interpolate(dragit.custom.line[vars.custom_trajectory].interpolate);

  dragit.evt.register = function(evt, f, d) {

    if (vars.dev)
      console.log('[register]', evt);

    if (typeof evt == 'string')
      evt = [evt];

    evt.forEach(function(e) {
      if (typeof vars.evt[e] == 'undefined')
        vars.evt[e] = [];

      vars.evt[e].push([ f, d ]);
    });
  };

  dragit.evt.call = function(evt, a) {

    if (vars.dev)
      console.log('[call]', evt, a);

    if (typeof vars.evt[evt] == 'undefined') {
      if (vars.dev)
        console.warn('No callback for event', evt, a);
      return;
    }

    vars.evt[evt].forEach(function(e) {
      if (vars.dev)
        console.log('[calling evt]', e);
      if (typeof (e[0]) != 'undefined')
        e[0](a);
    });
  };

  dragit.init = function(container) {

    dragit.time.offset = dragit.time.offset ? dragit.time.offset : 0;
    vars.container = d3.select(container);
  };

  dragit.trajectory.display = function(d, i, c) {

  // Making sure we do not display twice the same trajectory
    if (dragit.statemachine.current_state == 'drag' && dragit.statemachine.current_id == i)
      return;

    if (vars.dev)
      console.log('[display]', dragit.statemachine.current_state, dragit.statemachine.current_id, i);

    vars.gDragit = vars.container.insert('g', ':first-child')
      .attr('class', 'gDragit');

    if (typeof c != 'undefined' && c != 0) {
      vars.gDragit.classed(c, true);
    } else {
      vars.gDragit.classed('focus', true);
    }

    dragit.lineTrajectory = vars.gDragit.selectAll('.lineTrajectory')
      .data([dragit.data[i]])
      .enter().append('path')
      .attr('class', 'lineTrajectory')
      .attr('d', vars.svgLine.interpolate(dragit.custom.line[vars.custom_trajectory].interpolate));

    dragit.pointTrajectory = vars.gDragit.selectAll('.pointTrajectory')
      .data(dragit.data[i])
      .enter().append(dragit.custom.point[vars.custom_focus].mark)
      .attr('class', 'pointTrajectory')
      .attr(dragit.custom.point[vars.custom_focus].attr);

    return dragit.trajectory.displayUpdate(d, i);
  };

  dragit.trajectory.displayUpdate = function(d, i) {

    dragit.lineTrajectory.data([dragit.data[i]])
      .transition()
      .duration(0)
      .attr('d', vars.svgLine);

    dragit.pointTrajectory.data(dragit.data[i])
      .transition()
      .duration(0)
      .attr(dragit.custom.point[vars.custom_focus].attr);

    return dragit.lineTrajectory;
  };

  dragit.trajectory.toggleAll = function(c) {
    var c = c || '';
    var class_c = '';

    if (c.length > 0)
      class_c = '.' + c;
    if (d3.selectAll('.gDragit' + class_c)[0].length > 0)
      dragit.trajectory.removeAll(c);
    else
      dragit.trajectory.displayAll(c);
  };

  dragit.trajectory.displayAll = function(c) {
    var c = c || '';

    dragit.data.map(function(d, i) {
      dragit.trajectory.display({}, i, c);
    });
  };

  dragit.trajectory.remove = function(d, i) {
    if (dragit.statemachine.current_state != 'drag')
      d3.selectAll('.gDragit.focus').remove();
  };

  dragit.trajectory.removeAll = function(c) {
    var c = c || 'focus';

    d3.selectAll('.gDragit.' + c).remove();
  };

  // Main function that binds drag callbacks to the current element
  dragit.object.activate = function(d, i) {

    if (vars.dev)
      console.log('[activate]', d, i);


    d3.select(this)[0][0].node().addEventListener('mouseenter', function() {
      if (dragit.statemachine.current_state == 'idle') {
        dragit.statemachine.setState('mouseenter');
      }
    }, false);

    d3.select(this)[0][0].node().addEventListener('mouseleave', function() {
      if (dragit.statemachine.current_state == 'idle')
        dragit.statemachine.setState('mouseleave');
    }, false);

    d.call(d3.behavior.drag()
      .on('dragstart', function(d, i) {

        d3.event.sourceEvent.stopPropagation();
        dragit.statemachine.setState('dragstart');

        if (vars.dev)
          console.log('[dragstart]', d, i);

        dragit.trajectory.index_closest_trajectorypoint = -1;
        dragit.trajectory.index_closest_datapoint = -1;
        // Initial coordinates for the dragged object of interest
        d.x = 0;
        d.y = 0;

        switch (dragit.mouse.dragging) {
          case 'free':
          case 'horizontal':
        }

        var mousepoint = [ d3.mouse(this)[0] + dragit.object.offsetX, d3.mouse(this)[1] + dragit.object.offsetY ];

        // Create the line guide to closest trajectory
        dragit.lineClosestTrajectory = vars.gDragit.append('line')
          .attr('class', 'lineClosestTrajectory');

        // Create the line guide to closest point
        dragit.lineClosestPoint = vars.gDragit.append('line')
          .attr('class', 'lineClosestPoint');

        // Create the point interesting guide line and closest trajectory
        dragit.pointClosestTrajectory = vars.gDragit.append(dragit.custom.point[vars.custom_focus].mark)
          .attr(dragit.custom.point[vars.custom_focus].attr_static)
          .attr('class', 'pointClosestTrajectory')
          .attr('cx', mousepoint[0])
          .attr('cy', mousepoint[1]);

        // Create the focus that follows the mouse cursor
        dragit.focusGuide = vars.gDragit.append(dragit.custom.point[vars.custom_focus].mark)
          .attr(dragit.custom.point[vars.custom_focus].attr_static)
          .attr('class', 'focusGuide')
          .attr('cx', mousepoint[0])
          .attr('cy', mousepoint[1]);

        dragit.evt.call('dragstart');

      })
      .on('drag', function(d, i) {

        d3.event.sourceEvent.stopPropagation();
        dragit.time.previous = dragit.time.current;
        dragit.statemachine.setState('drag');

        var mousepoint = [ d3.event.x + dragit.object.offsetX, d3.event.y + dragit.object.offsetY ];

        if (vars.dev)
          console.log('[drag]', d, i);

        switch (dragit.mouse.dragging) {

          case 'free':

            d3.select(this).attr('transform', function(d, i) {
              return 'translate(' + [ mousepoint[0], mousepoint[1] ] + ')';
            });

            dragit.evt.call('drag');

            return;

          case 'horizontal':

            d.x += d3.event.dx;
            d.y = dragit.utils.findYgivenX(d.x, dragit.lineTrajectory);

            d3.select(this).attr('transform', function(d, i) {
              return 'translate(' + [ d.x, d.y ] + ')';
            });

            return;

        }

        var list_distances_datapoint = [],
            list_distances_trajectorypoint = [],
            list_times = [];
        var list_closest_trajectorypoint = [],
            list_closest_datapoint = [];

        var new_id = -1;

        // Browse all the .lineTrajectory trajectories
        // If scope is focus: only current trajectory is inspected
        // If scope is selected: all trajectories are inspected
        d3.selectAll('.' + dragit.mouse.scope).selectAll('.lineTrajectory').forEach(function(e, j) {

          var thisTrajectory = d3.select(e[0]);

          var current_index = null;

          if (dragit.mouse.scope == 'focus') {
            current_index = i;
          } else if (dragit.mouse.scope == 'selected') {
            current_index = j;
          }

          var closest_trajectorypoint = dragit.utils.closestPointToTrajectory(thisTrajectory.node(), mousepoint);

          var closest_datapoints = dragit.utils.closestDataPoint(mousepoint, dragit.data[current_index]);

          var index_closest_time = closest_datapoints.indexOf(Math.min.apply(Math, closest_datapoints));// + dragit.time.min;

          // Find the closest data point
          var closest_datapoint = dragit.data[current_index][index_closest_time];

          list_closest_trajectorypoint.push(closest_trajectorypoint.concat([current_index]));
          list_closest_datapoint.push(closest_datapoint.concat([current_index]));

          // Store all the closest distances between the mouse and the current trajectory point
          // Will be further used to find out the closest index (if scope is broader than 1 trajectory)
          list_distances_datapoint.push(Math.sqrt((closest_datapoint[0] - mousepoint[0]) * (closest_datapoint[0] - mousepoint[0]) + (closest_datapoint[1] - mousepoint[1]) * (closest_datapoint[1] - mousepoint[1])));
          list_distances_trajectorypoint.push(Math.sqrt((closest_trajectorypoint[0] - mousepoint[0]) * (closest_trajectorypoint[0] - mousepoint[0]) + (closest_trajectorypoint[1] - mousepoint[1]) * (closest_trajectorypoint[1] - mousepoint[1])));

          // Store the list of all closest times (one per trajectory)
          list_times.push(index_closest_time);

        });

        // Find the index of the closest trajectory by looking at the shortest distance
        // index_min should be used to retrieve the dragit.data[min_index] data
        var index_closest_datapoint = list_distances_datapoint.indexOf(d3.min(list_distances_datapoint));
        var index_closest_trajectorypoint = list_distances_trajectorypoint.indexOf(d3.min(list_distances_trajectorypoint));

        // It can happens the trajectory is not fully displayed yet, then leave because no closest one
        if (index_closest_trajectorypoint == -1)
          return;

        var new_time = list_times[index_closest_datapoint];

        // Update the line guide to closest trajectory
        dragit.lineClosestTrajectory.attr('x1', list_closest_trajectorypoint[index_closest_trajectorypoint][0])
          .attr('y1', list_closest_trajectorypoint[index_closest_trajectorypoint][1])
          .attr('x2', mousepoint[0])
          .attr('y2', mousepoint[1]);

        // Update the point interesting guide line and closest trajectory
        dragit.pointClosestTrajectory.attr('cx', list_closest_trajectorypoint[index_closest_trajectorypoint][0])
          .attr('cy', list_closest_trajectorypoint[index_closest_trajectorypoint][1]);

        // Update line guide to closest point
        dragit.lineClosestPoint.attr('x1', list_closest_datapoint[index_closest_datapoint][0])
          .attr('y1', list_closest_datapoint[index_closest_datapoint][1])
          .attr('x2', mousepoint[0])
          .attr('y2', mousepoint[1]);

        // Update the focus that follows the mouse cursor
        dragit.focusGuide.attr('cx', mousepoint[0])
          .attr('cy', mousepoint[1]);


        if (dragit.object.dragging == 'relative') {
          svg.style('cursor', 'none');
          // console.log("relative", list_closest_trajectorypoint[index_closest_trajectorypoint][0])

        }

        // We have a new time point
        if (dragit.time.current != new_time || dragit.trajectory.current_id != index_closest_trajectorypoint) {
          dragit.trajectory.index_closest_trajectorypoint = index_closest_trajectorypoint;
          dragit.time.current = new_time;
          dragit.evt.call('update', new_time, 0);
        }

        // We have a new trajectoy focus
        if (dragit.statemachine.current_id != index_closest_trajectorypoint && dragit.mouse.scope != 'focus') {
          dragit.statemachine.current_id = index_closest_trajectorypoint;
          dragit.evt.call('new_focus', dragit.statemachine.current_id);
        }

        dragit.evt.call('drag');

      })
      .on('dragend', function(d, i) {

        d3.event.sourceEvent.stopPropagation();
        dragit.statemachine.setState('dragend');

        if (vars.dev)
          console.log('[dragend]', d, i);

        switch (dragit.mouse.dragging) {

          case 'free':

            d3.select(this).transition()
              .duration(200)
              .attr('transform', function(d, i) {
                return 'translate(' + [ dragit.data[dragit.statemachine.current_id][dragit.time.current][0], dragit.data[dragit.statemachine.current_id][dragit.time.current][1] ] + ')';
              });
            break;

          case 'horizontal':
            break;
        }

        dragit.lineClosestTrajectory.remove();
        dragit.lineClosestPoint.remove();
        dragit.pointClosestTrajectory.remove();
        dragit.focusGuide.remove();

        // Remove the current focus trajectory
        d3.selectAll('.gDragit.focus').remove();

        dragit.evt.call('dragend');

        dragit.statemachine.setState('idle');
      })

    );
  };

  dragit.statemachine.setState = function(state) {

    if (vars.dev)
      console.log('[setState]', state);

    dragit.statemachine.current_state = state;
    dragit.evt.call('new_state');
  };

  dragit.statemachine.getState = function(state) {

    return dragit.statemachine.current_state;
  };

  dragit.playback.play = function() {

    if (dragit.playback.playing) {
      setTimeout(function() {

        if (!dragit.playback.playing)
          return;

        dragit.time.current++;

        dragit.evt.call('update', 0, 0);

        if (dragit.time.current == dragit.time.max - 1) {
          if (dragit.playback.loop) {
            dragit.time.current = 0;
            dragit.playback.play();
          } else {
            dragit.playback.stop();
          }
        } else
          dragit.playback.play();

      }, dragit.playback.speed);
    }

    dragit.evt.call('play');
  };

  dragit.playback.start = function() {

    if (!dragit.playback.playing) {
      dragit.playback.playing = true;
      d3.select(vars.playback.el).select('button').text('| |').attr('class', 'playing');

      if (dragit.time.current == dragit.time.max)
        dragit.time.current;

      dragit.playback.play();
    }
  };

  dragit.playback.stop = function() {
    d3.select(vars.playback.el).select('button').text('▶').attr('class', 'stop');
    dragit.playback.playing = false;
  };

  // Create and add a DOM HTML slider for time navigation
  dragit.utils.slider = function(el, play_button) {
    vars.playback.el = el;
    d3.select(el).append('p')
      .style('clear', 'both');

    if (play_button) {
      d3.select(el).append('button')
        .style({'height': '25px', 'width': '25px'})
        .text('▶')
        .attr('class', 'stop')
        .on('click', function() {
          if (dragit.playback.playing == false) {
            dragit.playback.start();
          } else {
            dragit.playback.stop();
          }
        });
    }

    d3.select(el).append('span')
      .attr('id', 'min-time')
      .text(dragit.time.min);

    d3.select(el).append('input')
      .attr('type', 'range')
      .attr('class', 'slider-time')
      .property('min', dragit.time.min)
      .property('max', dragit.time.max)
    //  .attr("step", 1)
      .on('input', function() {
        dragit.time.previous = dragit.time.current;
        dragit.time.current = parseInt(this.value) - dragit.time.min;
        dragit.evt.call('update', this.value, 0);
      });

    d3.select(el).append('span')
      .attr('id', 'max-time')
      .text(dragit.time.max);

    d3.select('.slider-time').property('value', dragit.time.current + dragit.time.min);

    dragit.evt.register('drag', function() {
      d3.select('.slider-time').property('value', dragit.time.current);
    });

  };

  dragit.utils.sliderUpdate = function(el) {
    d3.select(el).select('#max-time')
      .text(dragit.time.max);

    d3.select(el).select('.slider-time')
      .property('max', dragit.time.max)
      .property('value', dragit.time.current);
  };

  // Calculate the centroid of a given SVG element
  dragit.utils.centroid = function(s) {
    var e = selection.node(),
        bbox = e.getBBox();

    return [ bbox.x + bbox.width / 2, bbox.y + bbox.height / 2 ];
  };

  // Credits: http://bl.ocks.org/mbostock/8027637
  dragit.utils.closestPointToTrajectory = function(pathNode, point) {
    var pathLength = pathNode.getTotalLength(),
        precision = 8,
        best,
        bestLength,
        bestDistance = Infinity;

    // linear scan for coarse approximation
    for (var scan, scanLength = 0, scanDistance; scanLength <= pathLength; scanLength += precision) {
      if ((scanDistance = distance2(scan = pathNode.getPointAtLength(scanLength))) < bestDistance) {
        best = scan, bestLength = scanLength, bestDistance = scanDistance;
      }
    }

    // binary search for precise estimate
    precision /= 2;
    while (precision > 0.5) {
      var before,
          after,
          beforeLength,
          afterLength,
          beforeDistance,
          afterDistance;

      if ((beforeLength = bestLength - precision) >= 0 && (beforeDistance = distance2(before = pathNode.getPointAtLength(beforeLength))) < bestDistance) {
        best = before, bestLength = beforeLength, bestDistance = beforeDistance;
      } else if ((afterLength = bestLength + precision) <= pathLength && (afterDistance = distance2(after = pathNode.getPointAtLength(afterLength))) < bestDistance) {
        best = after, bestLength = afterLength, bestDistance = afterDistance;
      } else {
        precision /= 2;
      }
    }

    best = [ best.x, best.y ];
    best.distance = Math.sqrt(bestDistance);
    return best;

    function distance2(p) {
      var dx = p.x - point[0],
          dy = p.y - point[1];

      return dx * dx + dy * dy;
    }
  };

  dragit.utils.closestDataPoint = function(p, points) {
    var distances = points.map(function(d, i) {
      var dx = d[0] - p[0];
      var dy = d[1] - p[1];

      return Math.sqrt(dx * dx + dy * dy);
    });

    return distances;
  };

  // Code from http://bl.ocks.org/duopixel/3824661
  dragit.utils.findYgivenX = function(x, path) {
    var pathEl = path.node();
    var pathLength = pathEl.getTotalLength();
    var BBox = pathEl.getBBox();
    var scale = pathLength / BBox.width;
    var offsetLeft = document.getElementsByClassName('lineTrajectory')[0].offsetLeft;

    x = x - offsetLeft;

    var beginning = x,
        end = pathLength,
        target;

    while (true) {
      target = Math.floor((beginning + end) / 2);
      pos = pathEl.getPointAtLength(target);
      if ((target === end || target === beginning) && pos.x !== x) {
        break;
      }
      if (pos.x > x)
        end = target;
      else if (pos.x < x)
        beginning = target;
      else
        break;
    }
    return pos.y - 200;
  };

  dragit.utils.animateTrajectory = function(path, start_time, duration) {

    var totalLength = path.node().getTotalLength();

    path.attr('stroke-width', '5')
      .attr('stroke-dasharray', totalLength + ' ' + totalLength)
      .attr('stroke-dashoffset', totalLength)
      .transition()
      .duration(duration)
      .ease('linear')
      .attr('stroke-dashoffset', 0);
  };

  // Credits: http://bl.ocks.org/mbostock/1705868
  dragit.utils.translateAlong = function(path, duration) {
    var l = path.node().getTotalLength();

    return function(d, i, a) {
      return function(t) {
        var p = path.node().getPointAtLength(t * l);

        return 'translate(' + p.x + ',' + p.y + ')';
      };
    };
  };

  dragit.utils.getSubPath = function(start_time, end_time) {

    sub_data = dragit.data[dragit.statemachine.current_id].filter(function(d, i) {
      return i >= start_time && i <= end_time;
    });

    dragit.subTrajectory = vars.gDragit.selectAll('.subTrajectory')
      .data([sub_data])
      .enter().append('path')
      .attr('class', 'subTrajectory')
      .style({'stroke': 'black', 'stroke-width': 4})
      .attr('d', vars.svgLine.interpolate(dragit.custom.line[vars.custom_trajectory].interpolate));

    return dragit.subTrajectory;

  };

})();

Array.prototype.equals = function(b) {
  var a = this;
  var i = a.length;

  if (i != b.length)
    return false;
  while (i--) {
    if (a[i] !== b[i])
      return false;
  }
  return true;
};