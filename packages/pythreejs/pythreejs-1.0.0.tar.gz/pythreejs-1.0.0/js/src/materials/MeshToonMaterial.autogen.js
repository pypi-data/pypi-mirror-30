//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var MeshPhongMaterialModel = require('./MeshPhongMaterial.autogen.js').MeshPhongMaterialModel;

var TextureModel = require('../textures/Texture.autogen.js').TextureModel;

var MeshToonMaterialModel = MeshPhongMaterialModel.extend({

    defaults: function() {
        return _.extend(MeshPhongMaterialModel.prototype.defaults.call(this), {

            gradientMap: null,
            type: "MeshToonMaterial",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.MeshToonMaterial();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        MeshPhongMaterialModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('gradientMap');

        this.props_created_by_three['type'] = true;

        this.property_converters['gradientMap'] = 'convertThreeType';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'MeshToonMaterialModel',

    serializers: _.extend({
        gradientMap: { deserialize: widgets.unpack_models },
    },  MeshPhongMaterialModel.serializers),
});

module.exports = {
    MeshToonMaterialModel: MeshToonMaterialModel,
};
