//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var LightShadowModel = require('./LightShadow.js').LightShadowModel;


var DirectionalLightShadowModel = LightShadowModel.extend({

    defaults: function() {
        return _.extend(LightShadowModel.prototype.defaults.call(this), {


        });
    },

    constructThreeObject: function() {

        var result = new THREE.DirectionalLightShadow();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        LightShadowModel.prototype.createPropertiesArrays.call(this);




    },

}, {

    model_name: 'DirectionalLightShadowModel',

    serializers: _.extend({
    },  LightShadowModel.serializers),
});

module.exports = {
    DirectionalLightShadowModel: DirectionalLightShadowModel,
};
