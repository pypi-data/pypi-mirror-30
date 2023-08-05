//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ShaderMaterialModel = require('./ShaderMaterial.autogen.js').ShaderMaterialModel;


var RawShaderMaterialModel = ShaderMaterialModel.extend({

    defaults: function() {
        return _.extend(ShaderMaterialModel.prototype.defaults.call(this), {

            type: "RawShaderMaterial",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.RawShaderMaterial(
            {
                type: this.get('type'),
            }
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ShaderMaterialModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['extensions'] = true;
        this.props_created_by_three['type'] = true;

        this.property_converters['type'] = null;


    },

}, {

    model_name: 'RawShaderMaterialModel',

    serializers: _.extend({
    },  ShaderMaterialModel.serializers),
});

module.exports = {
    RawShaderMaterialModel: RawShaderMaterialModel,
};
