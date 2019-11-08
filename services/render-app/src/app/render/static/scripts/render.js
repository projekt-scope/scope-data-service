var clickedItem = "";
var uri = "";
var camera, scene, renderer, object, stats, container, shape_material;
var mouseX = 0;
var mouseXOnMouseDown = 0;
var mouseY = 0;
var mouseYOnMouseDown = 0;
var moveForward = false;
var moveBackward = false;
var moveLeft = false;
var moveRight = false;
var moveUp = false;
var moveDown = false;
var canvas;

container = document.getElementById("render")

CANVAS_WIDTH = container.clientWidth;
CANVAS_HEIGHT = window.innerHeight;

var windowHalfX = CANVAS_WIDTH / 2;
var windowHalfY = CANVAS_HEIGHT / 2;
var liste = [];
var selected_target_color_r = 0;
var selected_target_color_g = 0;
var selected_target_color_b = 0;
var selected_target = null;


init();
animate();

function init() {
    //     container = document.createElement('div');
    //    document.body.appendChild(container);


    container = document.getElementById("render")

    camera = new THREE.PerspectiveCamera(50, CANVAS_WIDTH / CANVAS_HEIGHT, 1, 200);

    camera.position.z = 100;
    // camera = new THREE.OrthographicCamera( window.innerWidth / - 2, window.innerWidth / 2, window.innerHeight / 2, window.innerHeight / - 2, 1, 1000 );

    // controls = new THREE.OrbitControls(camera);
    //controls = new THREE.OrbitControls(camera);
    // for selection
    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();
    // create scene
    scene = new THREE.Scene();
    add_light();

    loader = new THREE.BufferGeometryLoader();


    var last_element = jsonNameList[jsonNameList.length - 1];
    //console.log(last_element)


    loadJsons();

    //unsure what this does 

    // loader.load('<built-in function hash>.json', function(geometry) {
    // line_material = new THREE.LineBasicMaterial({color: 0x000000, linewidth: 2.0});
    // line = new THREE.Line(geometry, line_material);
    // scene.add(line);
    // });

    renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true
    });
    //Set the render size 
    // renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setSize(CANVAS_WIDTH, CANVAS_HEIGHT);
    //renderer.setPixelRatio(window.devicePixelRatio); 
    canvas = renderer.domElement;
    canvas.id = "canvas";


    container.appendChild(canvas);
    //renderer.gammaInput = true;
    //renderer.gammaOutput = true;
    // for shadow rendering
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    controls = new THREE.TrackballControls(camera, renderer.domElement);

    fit_to_scene();
    // show stats, is it really useful ?
    // stats = new Stats();
    // stats.domElement.style.position = 'absolute';
    // stats.domElement.style.top = '2%';
    // stats.domElement.style.left = '1%';
    // container.appendChild(stats.domElement);

    // add events
    // document.addEventListener('keypress', onDocumentKeyPress, false);
    document.addEventListener('click', onDocumentMouseClick, false);
    window.addEventListener('resize', onWindowResize, false);



}


function animate() {
    requestAnimationFrame(animate);
    controls.update();
    render();
}

function update_lights() {
    if (directionalLight != undefined) {
        directionalLight.position.copy(camera.position);
    }
}

function onWindowResize() {
    camera.aspect = CANVAS_WIDTH / CANVAS_HEIGHT;
    camera.updateProjectionMatrix();
    renderer.setSize(CANVAS_WIDTH, CANVAS_HEIGHT);

}


function onDocumentMouseClick(event) {


    // event.preventDefault();
    // https://stackoverflow.com/questions/36880033/clicking-objects-in-three-js-when-the-canvas-is-not-full-screen-r74
    var canvasBounds = renderer.context.canvas.getBoundingClientRect();

    mouse.x = ((event.clientX - canvasBounds.left) / (canvasBounds.right - canvasBounds.left)) * 2 - 1;
    mouse.y = -((event.clientY - canvasBounds.top) / (canvasBounds.bottom - canvasBounds.top)) * 2 + 1;


    if (Math.abs(mouse.x) <= 1 && Math.abs(mouse.y)) {

        // perform selection
        raycaster.setFromCamera(mouse, camera);
        var intersects = raycaster.intersectObjects(scene.children);
        if (intersects.length > 0) {
            // restore previous selected target color
            if (selected_target) {
                selected_target.material.color.setRGB(selected_target_color_r,
                    selected_target_color_g,
                    selected_target_color_b);
            }
            var target = intersects[0].object;
            selected_target_color_r = target.material.color.r;
            selected_target_color_g = target.material.color.g;
            selected_target_color_b = target.material.color.b;
            target.material.color.setRGB(1., 0.65, 0.);
            // console.log(target);
            // console.log(target.uuid);

            var found = false;
            // finde uri for uuid
            for (i in liste) {
                if (liste[i].uuidmesh == target.uuid) {
                    uri = liste[i].graphUri;
                    found = true;
                }
            }
            if (found) {

                clickedItem = uri.split('#')[1];
                //ajax request to API to update graph
                // console.log($('#toggle-event').prop('checked'));
                // var simplifylist = $('#toggle-event').prop('checked');
                var simplifylist = false;

                if (ts) {
                    update_graph_with_uri_TS(uri, simplifylist);
                } else {
                    update_graph_with_uri(uri, simplifylist);
                }
            }
            selected_target = target;
        }
    }
}



function fit_to_scene() {
    // compute bounding sphere of whole scene
    var center = new THREE.Vector3(0, 0, 0);
    var radiuses = new Array();
    var positions = new Array();
    // compute center of all objects
    scene.traverse(function (child) {
        if (child instanceof THREE.Mesh) {
            child.geometry.computeBoundingBox();
            var box = child.geometry.boundingBox;
            var curCenter = new THREE.Vector3().copy(box.min).add(box.max).multiplyScalar(0.5);
            var radius = new THREE.Vector3().copy(box.max).distanceTo(box.min) / 2.;
            center.add(curCenter);
            positions.push(curCenter);
            radiuses.push(radius);
        }
    });
    if (radiuses.length > 0) {
        center.divideScalar(radiuses.length * 0.7);
    }
    var maxRad = 1.;
    // compute bounding radius
    for (var ichild = 0; ichild < radiuses.length; ++ichild) {
        var distToCenter = positions[ichild].distanceTo(center);
        var totalDist = distToCenter + radiuses[ichild];
        if (totalDist > maxRad) {
            maxRad = totalDist;
        }
    }
    maxRad = maxRad * 0.7; // otherwise the scene seems to be too far away
    camera.lookAt(center);
    var direction = new THREE.Vector3().copy(camera.position).sub(controls.target);
    var len = direction.length();
    direction.normalize();

    // compute new distance of camera to middle of scene to fit the object to screen
    var lnew = maxRad / Math.sin(camera.fov / 180. * Math.PI / 2.);
    direction.multiplyScalar(lnew);

    var pnew = new THREE.Vector3().copy(center).add(direction);
    // change near far values to avoid culling of objects 
    camera.position.set(pnew.x, pnew.y, pnew.z);
    camera.far = lnew * 50;
    camera.near = lnew * 50 * 0.001;
    camera.updateProjectionMatrix();
    controls.target = center;
    controls.update();
    // adds and adjust a grid helper if needed
    gridHelper = new THREE.GridHelper(maxRad * 4, 10)
    scene.add(gridHelper);
    gridHelper.visible = !gridHelper.visible;
    // axisHelper
    axisHelper = new THREE.AxesHelper(maxRad);
    scene.add(axisHelper);
}

function render() {
    //@IncrementTime@  TODO UNCOMMENT
    update_lights();
    renderer.render(scene, camera);
}

function add_light() {
    // function that adds light to the scene

    scene.add(new THREE.AmbientLight(0x101010));
    directionalLight = new THREE.DirectionalLight(0xffffff);
    directionalLight.position.x = 1;
    directionalLight.position.y = -1;
    directionalLight.position.z = 2;
    directionalLight.position.normalize();
    scene.add(directionalLight);
    light1 = new THREE.PointLight(0xffffff);
    scene.add(light1);
}


function setVisibility() {

    if (selected_target) {
        selected_target.material.visible = !selected_target.material.visible;
    }

}

function toggleGrid() {
    gridHelper.visible = !gridHelper.visible;
}

function toggleAxis() {
    axisHelper.visible = !axisHelper.visible;

}

function setWire() {

    if (selected_target) {
        selected_target.material.wireframe = !selected_target.material.wireframe;
    }

}

function delete_all() {
    while (scene.children.length > 0) {
        scene.remove(scene.children[0]);
    }
    add_light();
}

function loadJsons(bbox = false) {
    //load shapes from json with the jsonNameList (created in the beginning with jinja script)
    //console.log(jsonNameList)
    jsonNameList.forEach(element => {

        var jqxhr = $.getJSON('static/shapes/' + element + '.json', function () {
                // console.log("json request send!");
                document.getElementById("loader").style.display = "block";
            })
            .done(function (json) {
                //   console.log("data recieved");
                add2scene(json, bbox);
                document.getElementById("loader").style.display = "none";
            })
            .fail(function () {
                console.log("error in json request");
                document.getElementById("loader").style.display = "none";
            })
            .always(function () {
                //   console.log("complete");
            });
    });
}

function add2scene(json, bbox = false) {

    var geometry = loader.parse(json);
    if (bbox) {
        var geometry = new THREE.EdgesGeometry(geometry);

        var material = new THREE.LineBasicMaterial({
            color: 0xFF0000
        }); // red line color 

        var wireframe = new THREE.LineSegments(geometry, material);

        scene.add(wireframe);
        liste.push({
            "uuidmesh": wireframe.uuid,
            "graphUri": json.uuid
        });
    } else {
        material = new THREE.MeshPhongMaterial({
            color: 0xa5a5a5,
            specular: 0xffffff,
            shininess: 0.9,
        });

        mesh = new THREE.Mesh(geometry, material);
        // add to liste for later
        liste.push({
            "uuidmesh": mesh.uuid,
            "graphUri": json.uuid
        });

        scene.add(mesh);
    }
    //-- fit to scene should only be called once --// otherwise we have more than one axis etc
    fit_to_scene();
    update_lights();

}

$(document).on('click', '#openCallsList a', function () {
    var v = $(this).parent().text()
    document.getElementById("element").value = v;

    v = "https://projekt-scope.de/ontologies/BIM#" + v.split(":")[1]
    for (i in liste) {
        if (liste[i].graphUri == v) {
            for (var a in scene.children) {
                if (scene.children[a].uuid == liste[i].uuidmesh) {
                    if (selected_target) {
                        selected_target.material.color.setRGB(selected_target_color_r,
                            selected_target_color_g,
                            selected_target_color_b);
                    }
                    var target = scene.children[a];
                    selected_target_color_r = target.material.color.r;
                    selected_target_color_g = target.material.color.g;
                    selected_target_color_b = target.material.color.b;
                    target.material.color.setRGB(0.72, 0.06, 0.13);
                    selected_target = target;
                }
            }
        }
    }
    update_graph_with_uri_TS(v, false);
});