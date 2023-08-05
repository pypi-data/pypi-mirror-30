//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseGeometryModel = require('../core/BaseGeometry.autogen.js').BaseGeometryModel;

var ShapeModel = require('../extras/core/Shape.autogen.js').ShapeModel;

var ShapeGeometryModel = BaseGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseGeometryModel.prototype.defaults.call(this), {

            shapes: [],
            curveSegments: 12,
            material: 0,
            type: "ShapeGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.ShapeGeometry(
            this.convertThreeTypeArrayModelToThree(this.get('shapes'), 'shapes')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseGeometryModel.prototype.createPropertiesArrays.call(this);
        this.three_nested_properties.push('shapes');

        this.props_created_by_three['type'] = true;

        this.property_converters['shapes'] = 'convertThreeTypeArray';
        this.property_converters['curveSegments'] = null;
        this.property_converters['material'] = null;
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'ShapeGeometryModel',

    serializers: _.extend({
        shapes: { deserialize: widgets.unpack_models },
    },  BaseGeometryModel.serializers),
});

module.exports = {
    ShapeGeometryModel: ShapeGeometryModel,
};
