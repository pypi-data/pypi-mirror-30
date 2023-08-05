//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseGeometryModel = require('./BaseGeometry.autogen.js').BaseGeometryModel;

var BaseGeometryModel = require('./BaseGeometry.autogen.js').BaseGeometryModel;

var GeometryModel = BaseGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseGeometryModel.prototype.defaults.call(this), {

            vertices: [],
            colors: ["#ffffff"],
            faces: [],
            faceVertexUvs: [],
            lineDistances: [],
            morphTargets: [],
            morphNormals: [],
            skinWeights: [],
            skinIndices: [],
            _ref_geometry: null,
            _store_ref: false,
            type: "Geometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Geometry();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseGeometryModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('_ref_geometry');

        this.props_created_by_three['type'] = true;

        this.property_converters['vertices'] = 'convertVectorArray';
        this.property_converters['colors'] = 'convertColorArray';
        this.property_converters['faces'] = 'convertFaceArray';
        this.property_converters['faceVertexUvs'] = null;
        this.property_converters['lineDistances'] = null;
        this.property_converters['morphTargets'] = null;
        this.property_converters['morphNormals'] = null;
        this.property_converters['skinWeights'] = 'convertVectorArray';
        this.property_converters['skinIndices'] = 'convertVectorArray';
        this.property_converters['_ref_geometry'] = 'convertThreeType';
        this.property_converters['_store_ref'] = 'convertBool';
        this.property_converters['type'] = null;

        this.property_assigners['vertices'] = 'assignArray';
        this.property_assigners['colors'] = 'assignArray';
        this.property_assigners['faces'] = 'assignArray';
        this.property_assigners['faceVertexUvs'] = 'assignArray';
        this.property_assigners['lineDistances'] = 'assignArray';
        this.property_assigners['morphTargets'] = 'assignArray';
        this.property_assigners['morphNormals'] = 'assignArray';
        this.property_assigners['skinWeights'] = 'assignArray';
        this.property_assigners['skinIndices'] = 'assignArray';

    },

}, {

    model_name: 'GeometryModel',

    serializers: _.extend({
        _ref_geometry: { deserialize: widgets.unpack_models },
    },  BaseGeometryModel.serializers),
});

module.exports = {
    GeometryModel: GeometryModel,
};
