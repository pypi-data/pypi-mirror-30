//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var Object3DModel = require('../core/Object3D.js').Object3DModel;

var Box3Model = require('../math/Box3.autogen.js').Box3Model;

var Box3HelperModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            box: null,
            color: "yellow",
            type: "Box3Helper",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Box3Helper(
            this.convertThreeTypeModelToThree(this.get('box'), 'box'),
            this.convertColorModelToThree(this.get('color'), 'color')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('box');

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['box'] = 'convertThreeType';
        this.property_converters['color'] = 'convertColor';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'Box3HelperModel',

    serializers: _.extend({
        box: { deserialize: widgets.unpack_models },
    },  Object3DModel.serializers),
});

module.exports = {
    Box3HelperModel: Box3HelperModel,
};
