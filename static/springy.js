/**
 * Springy v2.7.1
 *
 * Copyright (c) 2010-2013 Dennis Hotson, 2022 Mikael Honkala
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use,
 * copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following
 * conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 */
(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(function () {
            return (root.returnExportsGlobal = factory());
        });
    } else if (typeof exports === 'object') {
        // Node. Does not work with strict CommonJS, but
        // only CommonJS-like enviroments that support module.exports,
        // like Node.
        module.exports = factory();
    } else {
        // Browser globals
        root.Springy = factory();
    }
}(this, function() {

	var Springy = {};

	var Graph = Springy.Graph = function() {
		this.nodeSet = {};
		this.nodes = [];
		this.edges = [];
		this.adjacency = {};

		this.nextNodeId = 0;
		this.nextEdgeId = 0;
		this.eventListeners = [];
	};

	var Node = Springy.Node = function(id, data) {
		this.id = id;
		this.data = (data !== undefined) ? data : {};

	// Data fields used by layout algorithm in this file:
	// this.data.mass
	// Data used by default renderer in springyui.js
	// this.data.label
	};

	var Edge = Springy.Edge = function(id, source, target, data) {
		this.id = id;
		this.source = source;
		this.target = target;
		this.data = (data !== undefined) ? data : {};

	// Edge data field used by layout algorithm
	// this.data.length
	// this.data.type
	};

	Graph.prototype.addNode = function(node) {
		if (!(node.id in this.nodeSet)) {
			this.nodes.push(node);
		}

		this.nodeSet[node.id] = node;

		this.notify();
		return node;
	};

	Graph.prototype.addNodes = function() {
		// accepts variable number of arguments, where each argument
		// is a string that becomes both node identifier and label
		for (var i = 0; i < arguments.length; i++) {
			var name = arguments[i];
			var node = new Node(name, {label:name});
			this.addNode(node);
		}
	};

	Graph.prototype.addEdge = function(edge) {
		var exists = false;
		this.edges.forEach(function(e) {
			if (edge.id === e.id) { exists = true; }
		});

		if (!exists) {
			this.edges.push(edge);
		}

		if (!(edge.source.id in this.adjacency)) {
			this.adjacency[edge.source.id] = {};
		}
		if (!(edge.target.id in this.adjacency[edge.source.id])) {
			this.adjacency[edge.source.id][edge.target.id] = [];
		}

		exists = false;
		this.adjacency[edge.source.id][edge.target.id].forEach(function(e) {
				if (edge.id === e.id) { exists = true; }
		});

		if (!exists) {
			this.adjacency[edge.source.id][edge.target.id].push(edge);
		}

		this.notify();
		return edge;
	};

	Graph.prototype.addEdges = function() {
		// accepts variable number of arguments, where each argument
		// is a triple [nodeid1, nodeid2, attributes]
		for (var i = 0; i < arguments.length; i++) {
			var e = arguments[i];
			var node1 = this.nodeSet[e[0]];
			if (node1 == undefined) {
				throw new TypeError("invalid node name: " + e[0]);
			}
			var node2 = this.nodeSet[e[1]];
			if (node2 == undefined) {
				throw new TypeError("invalid node name: " + e[1]);
			}
			var attr = e[2];

			this.newEdge(node1, node2, attr);
		}
	};

	Graph.prototype.newNode = function(data) {
		var node = new Node(this.nextNodeId++, data);
		this.addNode(node);
		return node;
	};

	Graph.prototype.newEdge = function(source, target, data) {
		var edge = new Edge(this.nextEdgeId++, source, target, data);
		this.addEdge(edge);
		return edge;
	};

	// find the edges from node1 to node2
	Graph.prototype.getEdges = function(node1, node2) {
		if (node1.id in this.adjacency
			&& node2.id in this.adjacency[node1.id]) {
			return this.adjacency[node1.id][node2.id];
		}

		return [];
	};

	// remove a node and it's associated edges from the graph
	Graph.prototype.removeNode = function(node) {
		if (node.id in this.nodeSet) {
			delete this.nodeSet[node.id];
		}

		for (var i = this.nodes.length - 1; i >= 0; i--) {
			if (this.nodes[i].id === node.id) {
				this.nodes.splice(i, 1);
			}
		}

		this.detachNode(node);
	};

	// removes edges associated with a given node
	Graph.prototype.detachNode = function(node) {
		var tmpEdges = this.edges.slice();
		tmpEdges.forEach(function(e) {
			if (e.source.id === node.id || e.target.id === node.id) {
				this.removeEdge(e);
			}
		}, this);

		this.notify();
	};

	// remove a node and it's associated edges from the graph
	Graph.prototype.removeEdge = function(edge) {
		for (var i = this.edges.length - 1; i >= 0; i--) {
			if (this.edges[i].id === edge.id) {
				this.edges.splice(i, 1);
			}
		}

		for (var x in this.adjacency) {
			for (var y in this.adjacency[x]) {
				var edges = this.adjacency[x][y];

				for (var j=edges.length - 1; j>=0; j--) {
					if (this.adjacency[x][y][j].id === edge.id) {
						this.adjacency[x][y].splice(j, 1);
					}
				}

				// Clean up empty edge arrays
				if (this.adjacency[x][y].length == 0) {
					delete this.adjacency[x][y];
				}
			}

			// Clean up empty objects
			if (isEmpty(this.adjacency[x])) {
				delete this.adjacency[x];
			}
		}

		this.notify();
	};

	/* Merge a list of nodes and edges into the current graph. eg.
	var o = {
		nodes: [
			{id: 123, data: {type: 'user', userid: 123, displayname: 'aaa'}},
			{id: 234, data: {type: 'user', userid: 234, displayname: 'bbb'}}
		],
		edges: [
			{from: 0, to: 1, type: 'submitted_design', directed: true, data: {weight: }}
		]
	}
	*/
	Graph.prototype.merge = function(data) {
		var nodes = [];
		data.nodes.forEach(function(n) {
			nodes.push(this.addNode(new Node(n.id, n.data)));
		}, this);

		data.edges.forEach(function(e) {
			var from = nodes[e.from];
			var to = nodes[e.to];

			var id = (e.directed)
				? (id = e.type + "-" + from.id + "-" + to.id)
				: (from.id < to.id) // normalise id for non-directed edges
					? e.type + "-" + from.id + "-" + to.id
					: e.type + "-" + to.id + "-" + from.id;

			var edge = this.addEdge(new Edge(id, from, to, e.data));
			edge.data.type = e.type;
		}, this);
	};

	Graph.prototype.filterNodes = function(fn) {
		var tmpNodes = this.nodes.slice();
		tmpNodes.forEach(function(n) {
			if (!fn(n)) {
				this.removeNode(n);
			}
		}, this);
	};

	Graph.prototype.filterEdges = function(fn) {
		var tmpEdges = this.edges.slice();
		tmpEdges.forEach(function(e) {
			if (!fn(e)) {
				this.removeEdge(e);
			}
		}, this);
	};


	Graph.prototype.addGraphListener = function(obj) {
		this.eventListeners.push(obj);
	};

	Graph.prototype.notify = function() {
		this.eventListeners.forEach(function(obj){
			obj.graphChanged();
		});
	};

	// -----------
	var Layout = Springy.Layout = {};
	Layout.ForceDirected = function(graph, stiffness, repulsion, damping, minEnergyThreshold, maxSpeed) {
		this.graph = graph;
		this.stiffness = stiffness; // spring stiffness constant
		this.repulsion = repulsion; // repulsion constant
		this.damping = damping; // velocity damping factor
		this.minEnergyThreshold = minEnergyThreshold || 0.01; //threshold used to determine render stop
		this.maxSpeed = maxSpeed || Infinity; // nodes aren't allowed to exceed this speed

		this.nodePoints = {}; // keep track of points associated with nodes
		this.edgeSprings = {}; // keep track of springs associated with edges

		this.selected = null;
	};

	Layout.ForceDirected.prototype.point = function(node) {
		if (!(node.id in this.nodePoints)) {
			var mass = (node.data.mass !== undefined) ? node.data.mass : 1.0;
			this.nodePoints[node.id] = new Layout.ForceDirected.Point(Vector.random(), mass);
		}

		return this.nodePoints[node.id];
	};

	Layout.ForceDirected.prototype.spring = function(edge) {
		if (!(edge.id in this.edgeSprings)) {
			var length = (edge.data.length !== undefined) ? edge.data.length : 1.0;

			var existingSpring = false;

			var from = this.graph.getEdges(edge.source, edge.target);
			from.forEach(function(e) {
				if (existingSpring === false && e.id in this.edgeSprings) {
					existingSpring = this.edgeSprings[e.id];
				}
			}, this);

			if (existingSpring !== false) {
				return new Layout.ForceDirected.Spring(existingSpring.point1, existingSpring.point2, 0.0, 0.0, edge.source, edge.target);
			}

			var to = this.graph.getEdges(edge.target, edge.source);
			from.forEach(function(e){
				if (existingSpring === false && e.id in this.edgeSprings) {
					existingSpring = this.edgeSprings[e.id];
				}
			}, this);

			if (existingSpring !== false) {
				return new Layout.ForceDirected.Spring(existingSpring.point2, existingSpring.point1, 0.0, 0.0, edge.source, edge.target);
			}

			this.edgeSprings[edge.id] = new Layout.ForceDirected.Spring(
				this.point(edge.source), this.point(edge.target), length, this.stiffness, edge.source, edge.target
			);
		}

		return this.edgeSprings[edge.id];
	};

	// callback should accept two arguments: Node, Point
	Layout.ForceDirected.prototype.eachNode = function(callback) {
		var t = this;
		this.graph.nodes.forEach(function(n){
			callback.call(t, n, t.point(n));
		});
	};

	// callback should accept two arguments: Edge, Spring
	Layout.ForceDirected.prototype.eachEdge = function(callback) {
		var t = this;
		this.graph.edges.forEach(function(e){
			callback.call(t, e, t.spring(e));
		});
	};

	// callback should accept one argument: Spring
	Layout.ForceDirected.prototype.eachSpring = function(callback) {
		var t = this;
		this.graph.edges.forEach(function(e){
			callback.call(t, t.spring(e));
		});
	};


	// Physics stuff
	Layout.ForceDirected.prototype.applyCoulombsLaw = function() {
		this.eachNode(function(n1, point1) {
			this.eachNode(function(n2, point2) {
				if (point1 !== point2)
				{
					const d = point1.p.subtract(point2.p);
					//const effectiveDistance = this.effectiveDistance(d, n1, n2);
					//const distance = effectiveDistance + 0.1; // avoid massive forces at small distances (and divide by zero)
					const distance = d.magnitude() + 0.1;
					const direction = d.normalise();

					// apply force to each end point, except selected which is left to gravitate to center
					if (n1 !== this.selected) {
						point1.applyForce(direction.multiply(this.repulsion).divide(distance * distance * 0.5));
					}
					if (n2 !== this.selected) {
						point2.applyForce(direction.multiply(this.repulsion).divide(distance * distance * -0.5));
					}
				}
			});
		});
	};

	Layout.ForceDirected.prototype.applyHookesLaw = function() {
		this.eachSpring(function(spring){
			const d = spring.point2.p.subtract(spring.point1.p); // the direction of the spring
			//const effectiveMagnitude = layout.effectiveDistance(d, spring.node1, spring.node2);
			//const displacement = spring.length - effectiveMagnitude;
			const displacement = spring.length - d.magnitude();
			const direction = d.normalise();

			// apply force to each end point, except if it is connected to selected node
			if (spring.node1 !== this.selected) {
				spring.point1.applyForce(direction.multiply(spring.k * displacement * -0.5));
			}
			if (spring.node2 !== this.selected) {
				spring.point2.applyForce(direction.multiply(spring.k * displacement * 0.5));
			}
		});
	};

	Layout.ForceDirected.prototype.attractToCentre = function() {
		this.eachNode(function(node, point) {
			var direction = point.p.multiply(-1.0);
			point.applyForce(direction.multiply(this.repulsion / 50.0));
		});
	};

	Layout.ForceDirected.prototype.effectiveDistance = function(originVector, node1, node2) {
		const originMagnitude = originVector.magnitude();
		if (node1.data.width == 0) {console.log(node1.name)}
		const node1Overlap = originVector.rectangleIntersectionMagnitude(node1.data.width || 0.1, node1.data.height || 0.1);
		const node2Overlap = originVector.rectangleIntersectionMagnitude(node2.data.width || 0.1, node2.data.height || 0.1);
		const distance = Math.max(0, originMagnitude - node1Overlap - node2Overlap);

		return distance;
	};

	Layout.ForceDirected.prototype.updateVelocity = function(timestep) {
		this.eachNode(function(node, point) {
			point.v = point.v.add(point.a.multiply(timestep)).multiply(this.damping);
			if (point.v.magnitude() > this.maxSpeed) {
			    point.v = point.v.normalise().multiply(this.maxSpeed);
			}
			point.a = new Vector(0,0);
		});
	};

	Layout.ForceDirected.prototype.updatePosition = function(timestep) {
		this.eachNode(function(node, point) {
			point.p = point.p.add(point.v.multiply(timestep));
		});
	};

	// Calculate the total kinetic energy of the system
	Layout.ForceDirected.prototype.totalEnergy = function(timestep) {
		var energy = 0.0;
		this.eachNode(function(node, point) {
			var speed = point.v.magnitude();
			energy += 0.5 * point.m * speed * speed;
		});

		return energy;
	};

	var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; }; // stolen from coffeescript, thanks jashkenas! ;-)

	Springy.requestAnimationFrame = __bind(this.requestAnimationFrame ||
		this.webkitRequestAnimationFrame ||
		this.mozRequestAnimationFrame ||
		this.oRequestAnimationFrame ||
		this.msRequestAnimationFrame ||
		(function(callback, element) {
			this.setTimeout(callback, 10);
		}), this);


	/**
	 * Start simulation if it's not running already.
	 * In case it's running then the call is ignored, and none of the callbacks passed is ever executed.
	 */
	Layout.ForceDirected.prototype.start = function(render, onRenderStop, onRenderStart) {
		var t = this;

		if (this._started) return;
		this._started = true;
		this._stop = false;

		if (onRenderStart !== undefined) { onRenderStart(); }

		Springy.requestAnimationFrame(function step() {
			t.tick(0.03);
			//t.tick(0.003);
			//this.cachedBoundingBox = layout.getBoundingBox();

			if (render !== undefined) {
				render();
			}

			// stop simulation when energy of the system goes below a threshold
			if (t._stop || t.totalEnergy() < t.minEnergyThreshold) {
				t._started = false;
				if (onRenderStop !== undefined) { onRenderStop(); }
			} else {
				Springy.requestAnimationFrame(step);
			}
		});
	};

	Layout.ForceDirected.prototype.stop = function() {
		this._stop = true;
	}

	Layout.ForceDirected.prototype.tick = function(timestep) {
		this.applyCoulombsLaw();
		this.applyHookesLaw();
		this.attractToCentre();
		this.updateVelocity(timestep);
		this.updatePosition(timestep);
	};

	// Find the nearest point to a particular position
	Layout.ForceDirected.prototype.nearest = function(pos) {
		var min = {node: null, point: null, distance: null};
		var t = this;
		this.graph.nodes.forEach(function(n){
			var point = t.point(n);
			var distance = point.p.subtract(pos).magnitude();

			if (min.distance === null || distance < min.distance) {
				min = {node: n, point: point, distance: distance};
			}
		});

		return min;
	};

	// returns [bottomleft, topright]
	Layout.ForceDirected.prototype.getBoundingBox = function() {
		var bottomleft = new Vector(-2,-2);
		var topright = new Vector(2,2);

		this.eachNode(function(n, point) {
			if (point.p.x < bottomleft.x) {
				bottomleft.x = point.p.x;
			}
			if (point.p.y < bottomleft.y) {
				bottomleft.y = point.p.y;
			}
			if (point.p.x > topright.x) {
				topright.x = point.p.x;
			}
			if (point.p.y > topright.y) {
				topright.y = point.p.y;
			}
		});

		var padding = topright.subtract(bottomleft).multiply(0.07); // ~5% padding

		return {bottomleft: bottomleft.subtract(padding), topright: topright.add(padding)};
	};


	// Vector
	var Vector = Springy.Vector = function(x, y) {
		this.x = x;
		this.y = y;
	};

	Vector.random = function() {
		return new Vector(10.0 * (Math.random() - 0.5), 10.0 * (Math.random() - 0.5));
	};

	Vector.prototype.add = function(v2) {
		return new Vector(this.x + v2.x, this.y + v2.y);
	};

	Vector.prototype.subtract = function(v2) {
		return new Vector(this.x - v2.x, this.y - v2.y);
	};

	Vector.prototype.multiply = function(n) {
		return new Vector(this.x * n, this.y * n);
	};

	Vector.prototype.divide = function(n) {
		return new Vector((this.x / n) || 0, (this.y / n) || 0); // Avoid divide by zero errors..
	};

	Vector.prototype.magnitude = function() {
		return Math.sqrt(this.x*this.x + this.y*this.y);
	};

	Vector.prototype.rectangleIntersectionMagnitude = function(width, height) {
		const radians = this.radians();
		const absCosAngle = Math.abs(Math.cos(radians));
        const absSinAngle = Math.abs(Math.sin(radians));

        if (width / 2 * absSinAngle <= height / 2 * absCosAngle) {
			return width / 2 / absCosAngle;
		} else {
			return height / 2 / absSinAngle;
		}
	};

	Vector.prototype.radians = function() {
		return Math.atan2(this.y, this.x);
	};

	Vector.prototype.normal = function() {
		return new Vector(-this.y, this.x);
	};

	Vector.prototype.normalise = function() {
		return this.divide(this.magnitude());
	};

	// Point
	Layout.ForceDirected.Point = function(position, mass) {
		this.p = position; // position
		this.m = mass; // mass
		this.v = new Vector(0, 0); // velocity
		this.a = new Vector(0, 0); // acceleration
	};

	Layout.ForceDirected.Point.prototype.applyForce = function(force) {
		this.a = this.a.add(force.divide(this.m));
	};

	// Spring
	Layout.ForceDirected.Spring = function(point1, point2, length, k, node1, node2) {
		this.point1 = point1;
		this.point2 = point2;
		this.length = length; // spring length at rest
		this.k = k; // spring constant (See Hooke's law) .. how stiff the spring is

		this.node1 = node1;
		this.node2 = node2;
	};

	// Layout.ForceDirected.Spring.prototype.distanceToPoint = function(point)
	// {
	// 	// hardcore vector arithmetic.. ohh yeah!
	// 	// .. see http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment/865080#865080
	// 	var n = this.point2.p.subtract(this.point1.p).normalise().normal();
	// 	var ac = point.p.subtract(this.point1.p);
	// 	return Math.abs(ac.x * n.x + ac.y * n.y);
	// };

	/**
	 * Renderer handles the layout rendering loop
	 * @param onRenderStop optional callback function that gets executed whenever rendering stops.
	 * @param onRenderStart optional callback function that gets executed whenever rendering starts.
	 * @param onRenderFrame optional callback function that gets executed after each frame is rendered.
	 */
	var Renderer = Springy.Renderer = function(layout, clear, drawEdge, drawNode, onRenderStop, onRenderStart, onRenderFrame) {
		this.layout = layout;
		this.clear = clear;
		this.drawEdge = drawEdge;
		this.drawNode = drawNode;
		this.onRenderStop = onRenderStop;
		this.onRenderStart = onRenderStart;
		this.onRenderFrame = onRenderFrame;

		this.layout.graph.addGraphListener(this);
	}

	Renderer.prototype.graphChanged = function(e) {
		this.start();
	};

	/**
	 * Starts the simulation of the layout in use.
	 *
	 * Note that in case the algorithm is still or already running then the layout that's in use
	 * might silently ignore the call, and your optional <code>done</code> callback is never executed.
	 * At least the built-in ForceDirected layout behaves in this way.
	 *
	 * @param done An optional callback function that gets executed when the springy algorithm stops,
	 * either because it ended or because stop() was called.
	 */
	Renderer.prototype.start = function(done) {
		var t = this;
		this.layout.start(function render() {
			t.clear();

			t.layout.eachEdge(function(edge, spring) {
				t.drawEdge(edge, spring.point1.p, spring.point2.p);
			});

			t.layout.eachNode(function(node, point) {
				t.drawNode(node, point.p);
			});

			if (t.onRenderFrame !== undefined) { t.onRenderFrame(); }
		}, this.onRenderStop, this.onRenderStart);
	};

	Renderer.prototype.stop = function() {
		this.layout.stop();
	};

	var isEmpty = function(obj) {
		for (var k in obj) {
			if (obj.hasOwnProperty(k)) {
				return false;
			}
		}
		return true;
	};

  return Springy;
}));