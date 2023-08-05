//
// This file auto-generated with generate-wrappers.js
//
// Load all three.js python wrappers
var loadedModules = [
    require('./ArrowHelper.autogen.js'),
    require('./AxesHelper.autogen.js'),
    require('./Box3Helper.autogen.js'),
    require('./BoxHelper.autogen.js'),
    require('./CameraHelper.autogen.js'),
    require('./DirectionalLightHelper.autogen.js'),
    require('./FaceNormalsHelper.autogen.js'),
    require('./GridHelper.autogen.js'),
    require('./HemisphereLightHelper.autogen.js'),
    require('./PlaneHelper.autogen.js'),
    require('./PointLightHelper.autogen.js'),
    require('./PolarGridHelper.autogen.js'),
    require('./RectAreaLightHelper.autogen.js'),
    require('./SkeletonHelper.autogen.js'),
    require('./SpotLightHelper.autogen.js'),
    require('./VertexNormalsHelper.autogen.js'),
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

