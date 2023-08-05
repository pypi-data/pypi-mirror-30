//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseGeometryModel = require('../core/BaseGeometry.autogen.js').BaseGeometryModel;


var PolyhedronGeometryModel = BaseGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseGeometryModel.prototype.defaults.call(this), {

            vertices: [],
            indices: [],
            radius: 1,
            detail: 0,
            faces: [],
            type: "PolyhedronGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.PolyhedronGeometry(
            this.get('vertices'),
            this.get('faces'),
            this.convertFloatModelToThree(this.get('radius'), 'radius'),
            this.convertFloatModelToThree(this.get('detail'), 'detail')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseGeometryModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['vertices'] = null;
        this.property_converters['indices'] = null;
        this.property_converters['radius'] = 'convertFloat';
        this.property_converters['detail'] = 'convertFloat';
        this.property_converters['faces'] = null;
        this.property_converters['type'] = null;

        this.property_assigners['vertices'] = 'assignArray';
        this.property_assigners['indices'] = 'assignArray';
        this.property_assigners['faces'] = 'assignArray';

    },

}, {

    model_name: 'PolyhedronGeometryModel',

    serializers: _.extend({
    },  BaseGeometryModel.serializers),
});

module.exports = {
    PolyhedronGeometryModel: PolyhedronGeometryModel,
};
