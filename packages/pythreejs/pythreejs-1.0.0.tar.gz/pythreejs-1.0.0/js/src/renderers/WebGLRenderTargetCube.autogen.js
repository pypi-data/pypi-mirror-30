//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;


var WebGLRenderTargetCubeModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {


        });
    },

    constructThreeObject: function() {

        var result = new THREE.WebGLRenderTargetCube();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);




    },

}, {

    model_name: 'WebGLRenderTargetCubeModel',

    serializers: _.extend({
    },  ThreeModel.serializers),
});

module.exports = {
    WebGLRenderTargetCubeModel: WebGLRenderTargetCubeModel,
};
