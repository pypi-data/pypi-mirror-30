//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var Object3DModel = require('../core/Object3D.js').Object3DModel;

var Object3DModel = require('../core/Object3D.js').Object3DModel;

var FaceNormalsHelperModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            object: null,
            size: 1,
            color: "0xffff00",
            linewidth: 1,
            type: "FaceNormalsHelper",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.FaceNormalsHelper(
            this.convertThreeTypeModelToThree(this.get('object'), 'object'),
            this.convertFloatModelToThree(this.get('size'), 'size'),
            this.convertColorModelToThree(this.get('color'), 'color'),
            this.convertFloatModelToThree(this.get('linewidth'), 'linewidth')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('object');

        this.props_created_by_three['matrixAutoUpdate'] = true;
        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['object'] = 'convertThreeType';
        this.property_converters['size'] = 'convertFloat';
        this.property_converters['color'] = 'convertColor';
        this.property_converters['linewidth'] = 'convertFloat';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'FaceNormalsHelperModel',

    serializers: _.extend({
        object: { deserialize: widgets.unpack_models },
    },  Object3DModel.serializers),
});

module.exports = {
    FaceNormalsHelperModel: FaceNormalsHelperModel,
};
