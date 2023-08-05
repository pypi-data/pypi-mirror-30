//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var Object3DModel = require('../core/Object3D.js').Object3DModel;

var SpriteMaterialModel = require('../materials/SpriteMaterial.autogen.js').SpriteMaterialModel;

var SpriteModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            material: null,
            center: [0.5,0.5],
            type: "Sprite",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Sprite(
            this.convertThreeTypeModelToThree(this.get('material'), 'material')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('material');

        this.props_created_by_three['skeleton'] = true;
        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['material'] = 'convertThreeType';
        this.property_converters['center'] = 'convertVector';
        this.property_converters['type'] = null;

        this.property_assigners['center'] = 'assignVector';

    },

}, {

    model_name: 'SpriteModel',

    serializers: _.extend({
        material: { deserialize: widgets.unpack_models },
    },  Object3DModel.serializers),
});

module.exports = {
    SpriteModel: SpriteModel,
};
