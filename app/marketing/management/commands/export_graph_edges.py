'''
    Copyright (C) 2021 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation,either version 3 of the License,or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not,see <http://www.gnu.org/licenses/>.

'''
import re

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

import pytz


def is_an_edge(handle, edges):
    for edge in edges:
        if handle == edge[0]:
            return True
        if handle == edge[1]:
            return True
    return False

def normalize_handle(handle):
    return re.sub(r'\W+', '', handle)


class Command(BaseCommand):

    help = 'exports graph visualizations for http://experiments.owocki.com/Graph-Visualization/all/simple_graph.js:L157'

    def add_arguments(self, parser):
        parser.add_argument('what', default='economics', type=str)

    def handle(self, *args, **options):
        # output me as simple_graph.js
        handles = []
        edges = []
        start_date = timezone.now()
        start_date = timezone.datetime(2020, 1, 1, 1, tzinfo=pytz.UTC)

        what = options['what']

        if what in ['all', 'economics']:
            from dashboard.models import BountyFulfillment
            for obj in BountyFulfillment.objects.filter(accepted=True, created_on__gt=start_date):
                handle1 = obj.bounty.bounty_owner_github_username
                handle2 = obj.fulfiller_github_username
                handles.append(handle1)
                handles.append(handle2)
                edges.append([handle1, handle2])

        if what in ['all', 'economics']:
            from dashboard.models import Tip
            for obj in Tip.objects.filter(network='mainnet', created_on__gt=start_date):
                handle1 = obj.from_username
                handle2 = obj.username
                handles.append(handle1)
                handles.append(handle2)
                edges.append([handle1, handle2])

        if what in ['all', 'economics']:
            from kudos.models import KudosTransfer
            for obj in KudosTransfer.objects.filter(network='mainnet', created_on__gt=start_date):
                handle1 = obj.from_username
                handle2 = obj.username
                handles.append(handle1)
                handles.append(handle2)
                edges.append([handle1, handle2])

        if what in ['all', 'economics', 'grants']:
            from grants.models import Contribution
            for obj in Contribution.objects.filter(subscription__network='mainnet', created_on__gt=start_date):
                handle1 = obj.subscription.grant.admin_profile.handle
                handle2 = obj.subscription.contributor_profile.handle
                handles.append(handle1)
                handles.append(handle2)
                edges.append([handle1, handle2])

        if what in ['all', 'social']:
            from quests.models import QuestAttempt
            for obj in QuestAttempt.objects.filter(created_on__gt=start_date):
                handle1 = obj.quest.title
                handle2 = obj.profile.handle
                handles.append(handle1)
                handles.append(handle2)
                edges.append([handle1, handle2])


        # assemble and output
        handles = set(handles)
        handles = [handle for handle in handles if is_an_edge(handle, edges)]
        print(header)
        counter = 1
        for handle in handles:
            if handle:
                handle = normalize_handle(handle)
                counter += 1
                print(f'var user_{handle} = new GRAPHVIS.Node({counter}); user_{handle}.data.title = "user_{handle}";  graph.addNode(user_{handle}); drawNode(user_{handle});')

        for edge in edges:
            handle1 = edge[0]
            handle2 = edge[1]
            handle1 = normalize_handle(handle1)
            handle2 = normalize_handle(handle2)
            if handle1 and handle2:
                print(f"graph.addEdge(user_{handle1}, user_{handle2}); drawEdge(user_{handle1}, user_{handle2}); ");

        print(footer)

header = """

var Drawing = Drawing || {};

Drawing.SimpleGraph = function(options) {
  options = options || {};

  this.layout = options.layout || "2d";
  this.layout_options = options.graphLayout || {};
  this.show_stats = options.showStats || false;
  this.show_info = options.showInfo || false;
  this.show_labels = options.showLabels || false;
  this.selection = options.selection || false;
  this.limit = options.limit || 10;
  this.nodes_count = options.numNodes || 20;
  this.edges_count = options.numEdges || 10;
  this.show_labels = true;

  var camera, controls, scene, renderer, interaction, geometry, object_selection;
  var stats;
  var info_text = {};
  var graph = new GRAPHVIS.Graph({limit: options.limit});

  var geometries = [];

  var that=this;

  init();
  createGraph();
  animate();

  function init() {
    // Three.js initialization
    renderer = new THREE.WebGLRenderer({alpha: true, antialias: true});
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);


    camera = new THREE.PerspectiveCamera(40, window.innerWidth/window.innerHeight, 1, 1000000);
    camera.position.z = 10000;

    controls = new THREE.TrackballControls(camera);

    controls.rotateSpeed = 0.5;
    controls.zoomSpeed = 5.2;
    controls.panSpeed = 1;

    controls.noZoom = false;
    controls.noPan = false;

    controls.staticMoving = false;
    controls.dynamicDampingFactor = 0.3;

    controls.keys = [ 65, 83, 68 ];

    controls.addEventListener('change', render);

    scene = new THREE.Scene();

    // Node geometry
    if(that.layout === "3d") {
      geometry = new THREE.SphereGeometry(30);
    } else {
      geometry = new THREE.BoxGeometry( 50, 50, 0 );
    }

    // Create node selection, if set
    if(that.selection) {
      object_selection = new THREE.ObjectSelection({
        domElement: renderer.domElement,
        selected: function(obj) {
          // display info
          if(obj !== null) {
            info_text.select = "Object " + obj.id;
          } else {
            delete info_text.select;
          }
        },
        clicked: function(obj) {
        }
      });
    }

    document.body.appendChild( renderer.domElement );

    // Stats.js
    if(that.show_stats) {
      stats = new Stats();
      stats.domElement.style.position = 'absolute';
      stats.domElement.style.top = '0px';
      document.body.appendChild( stats.domElement );
    }

    // Create info box
    if(that.show_info) {
      var info = document.createElement("div");
      var id_attr = document.createAttribute("id");
      id_attr.nodeValue = "graph-info";
      info.setAttributeNode(id_attr);
      document.body.appendChild( info );
    }
  }


  /**
   *  Creates a graph with random nodes and edges.
   *  Number of nodes and edges can be set with
   *  numNodes and numEdges.
   */
  function createGraph() {
"""

footer = """

    that.layout_options.width = that.layout_options.width || 2000;
    that.layout_options.height = that.layout_options.height || 2000;
    that.layout_options.iterations = that.layout_options.iterations || 100000;
    that.layout_options.layout = that.layout_options.layout || that.layout;
    graph.layout = new Layout.ForceDirected(graph, that.layout_options);
    graph.layout.init();
    info_text.nodes = "Nodes " + graph.nodes.length;
    info_text.edges = "Edges " + graph.edges.length;
  }


  /**
   *  Create a node object and add it to the scene.
   */
  function drawNode(node) {
    var draw_object = new THREE.Mesh( geometry, new THREE.MeshBasicMaterial( {  color: Math.random() * 0xe0e0e0, opacity: 0.8 } ) );
    var label_object;

    if(that.show_labels) {
      if(node.data.title !== undefined) {
        label_object = new THREE.Label(node.data.title);
      } else {
        label_object = new THREE.Label(node.id);
      }
      node.data.label_object = label_object;
      scene.add( node.data.label_object );
    }

    var area = 5000;
    draw_object.position.x = Math.floor(Math.random() * (area + area + 1) - area);
    draw_object.position.y = Math.floor(Math.random() * (area + area + 1) - area);

    if(that.layout === "3d") {
      draw_object.position.z = Math.floor(Math.random() * (area + area + 1) - area);
    }

    draw_object.id = node.id;
    node.data.draw_object = draw_object;
    node.position = draw_object.position;
    scene.add( node.data.draw_object );
  }


  /**
   *  Create an edge object (line) and add it to the scene.
   */
  function drawEdge(source, target) {
      material = new THREE.LineBasicMaterial({ color: 0x606060 });

      var tmp_geo = new THREE.Geometry();
      tmp_geo.vertices.push(source.data.draw_object.position);
      tmp_geo.vertices.push(target.data.draw_object.position);

      line = new THREE.LineSegments( tmp_geo, material );
      line.scale.x = line.scale.y = line.scale.z = 1;
      line.originalScale = 1;

      // NOTE: Deactivated frustumCulled, otherwise it will not draw all lines (even though
      // it looks like the lines are in the view frustum).
      line.frustumCulled = false;

      geometries.push(tmp_geo);

      scene.add( line );
  }


  function animate() {
    requestAnimationFrame( animate );
    controls.update();
    render();
    if(that.show_info) {
      printInfo();
    }
  }


  function render() {
    var i, length, node;

    // Generate layout if not finished
    if(!graph.layout.finished) {
      info_text.calc = "<span style='color: red'>Calculating layout...</span>";
      graph.layout.generate();
    } else {
      info_text.calc = "";
    }

    // Update position of lines (edges)
    for(i=0; i<geometries.length; i++) {
      geometries[i].verticesNeedUpdate = true;
    }


    // Show labels if set
    // It creates the labels when this options is set during visualization
    if(that.show_labels) {
      length = graph.nodes.length;
      for(i=0; i<length; i++) {
        node = graph.nodes[i];
        if(node.data.label_object !== undefined) {
          node.data.label_object.position.x = node.data.draw_object.position.x;
          node.data.label_object.position.y = node.data.draw_object.position.y - 100;
          node.data.label_object.position.z = node.data.draw_object.position.z;
          node.data.label_object.lookAt(camera.position);
        } else {
          var label_object;
          if(node.data.title !== undefined) {
            label_object = new THREE.Label(node.data.title, node.data.draw_object);
          } else {
            label_object = new THREE.Label(node.id, node.data.draw_object);
          }
          node.data.label_object = label_object;
          scene.add( node.data.label_object );
        }
      }
    } else {
      length = graph.nodes.length;
      for(i=0; i<length; i++) {
        node = graph.nodes[i];
        if(node.data.label_object !== undefined) {
          scene.remove( node.data.label_object );
          node.data.label_object = undefined;
        }
      }
    }

    // render selection
    if(that.selection) {
      object_selection.render(scene, camera);
    }

    // update stats
    if(that.show_stats) {
      stats.update();
    }

    // render scene
    renderer.render( scene, camera );
  }

  /**
   *  Prints info from the attribute info_text.
   */
  function printInfo(text) {
    var str = '';
    for(var index in info_text) {
      if(str !== '' && info_text[index] !== '') {
        str += " - ";
      }
      str += info_text[index];
    }
    document.getElementById("graph-info").innerHTML = str;
  }

  // Generate random number
  function randomFromTo(from, to) {
    return Math.floor(Math.random() * (to - from + 1) + from);
  }

  // Stop layout calculation
  this.stop_calculating = function() {
    graph.layout.stop_calculating();
  };
};

"""
