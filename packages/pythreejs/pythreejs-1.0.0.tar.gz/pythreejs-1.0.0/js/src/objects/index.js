//
// This file auto-generated with generate-wrappers.js
//
// Load all three.js python wrappers
var loadedModules = [
    require('./Blackbox.js'),
    require('./Bone.autogen.js'),
    require('./CloneArray.js'),
    require('./Group.autogen.js'),
    require('./LOD.autogen.js'),
    require('./Line.autogen.js'),
    require('./LineLoop.autogen.js'),
    require('./LineSegments.autogen.js'),
    require('./Mesh.js'),
    require('./Points.autogen.js'),
    require('./Skeleton.autogen.js'),
    require('./SkinnedMesh.js'),
    require('./Sprite.autogen.js'),
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

