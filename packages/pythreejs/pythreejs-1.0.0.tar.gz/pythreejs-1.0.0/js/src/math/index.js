//
// This file auto-generated with generate-wrappers.js
//
// Load all three.js python wrappers
var loadedModules = [
    require('./Box2.autogen.js'),
    require('./Box3.autogen.js'),
    require('./Cylindrical.autogen.js'),
    require('./Frustum.autogen.js'),
    require('./Interpolant.autogen.js'),
    require('./Line3.autogen.js'),
    require('./Math.autogen.js'),
    require('./Plane.autogen.js'),
    require('./Quaternion.autogen.js'),
    require('./Ray.autogen.js'),
    require('./Sphere.autogen.js'),
    require('./Spherical.autogen.js'),
    require('./Triangle.autogen.js'),
    require('./interpolants'),
];

for (var i in loadedModules) {
    if (loadedModules.hasOwnProperty(i)) {
        var loadedModule = loadedModules[i];
        for (var target_name in loadedModule) {
            if (loadedModule.hasOwnProperty(target_name)) {
                module.exports[target_name] = loadedModule[target_name];
            }
        }
    }
}

