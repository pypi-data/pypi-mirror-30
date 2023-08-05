//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseGeometryModel = require('../core/BaseGeometry.autogen.js').BaseGeometryModel;


var LatheGeometryModel = BaseGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseGeometryModel.prototype.defaults.call(this), {

            points: [],
            segments: 12,
            phiStart: 0,
            phiLength: 6.283185307179586,
            type: "LatheGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.LatheGeometry(
            this.convertVectorArrayModelToThree(this.get('points'), 'points'),
            this.get('segments'),
            this.convertFloatModelToThree(this.get('phiStart'), 'phiStart'),
            this.convertFloatModelToThree(this.get('phiLength'), 'phiLength')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseGeometryModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['points'] = 'convertVectorArray';
        this.property_converters['segments'] = null;
        this.property_converters['phiStart'] = 'convertFloat';
        this.property_converters['phiLength'] = 'convertFloat';
        this.property_converters['type'] = null;

        this.property_assigners['points'] = 'assignArray';

    },

}, {

    model_name: 'LatheGeometryModel',

    serializers: _.extend({
    },  BaseGeometryModel.serializers),
});

module.exports = {
    LatheGeometryModel: LatheGeometryModel,
};
