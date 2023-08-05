//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var Object3DModel = require('../core/Object3D.js').Object3DModel;

var FogModel = require('./Fog.autogen.js').FogModel;
var MaterialModel = require('../materials/Material.js').MaterialModel;

var SceneModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            fog: null,
            overrideMaterial: null,
            autoUpdate: true,
            background: "#ffffff",
            type: "Scene",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Scene();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('fog');
        this.three_properties.push('overrideMaterial');

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['fog'] = 'convertThreeType';
        this.property_converters['overrideMaterial'] = 'convertThreeType';
        this.property_converters['autoUpdate'] = 'convertBool';
        this.property_converters['background'] = 'convertColor';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'SceneModel',

    serializers: _.extend({
        fog: { deserialize: widgets.unpack_models },
        overrideMaterial: { deserialize: widgets.unpack_models },
    },  Object3DModel.serializers),
});

module.exports = {
    SceneModel: SceneModel,
};
