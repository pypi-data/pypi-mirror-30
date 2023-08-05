//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var Object3DModel = require('../core/Object3D.js').Object3DModel;

var Object3DModel = require('../core/Object3D.js').Object3DModel;

var CloneArrayModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            original: null,
            positions: [],
            merge: false,
            type: "CloneArray",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.CloneArray(
            this.convertThreeTypeModelToThree(this.get('original'), 'original'),
            this.convertVectorArrayModelToThree(this.get('positions'), 'positions'),
            this.convertBoolModelToThree(this.get('merge'), 'merge')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('original');

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['original'] = 'convertThreeType';
        this.property_converters['positions'] = 'convertVectorArray';
        this.property_converters['merge'] = 'convertBool';
        this.property_converters['type'] = null;

        this.property_assigners['positions'] = 'assignArray';

    },

}, {

    model_name: 'CloneArrayModel',

    serializers: _.extend({
        original: { deserialize: widgets.unpack_models },
    },  Object3DModel.serializers),
});

module.exports = {
    CloneArrayModel: CloneArrayModel,
};
