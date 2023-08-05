//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseGeometryModel = require('../core/BaseGeometry.autogen.js').BaseGeometryModel;


var TorusKnotGeometryModel = BaseGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseGeometryModel.prototype.defaults.call(this), {

            radius: 1,
            tube: 0.4,
            tubularSegments: 64,
            radialSegments: 8,
            p: 2,
            q: 3,
            type: "TorusKnotGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.TorusKnotGeometry(
            this.convertFloatModelToThree(this.get('radius'), 'radius'),
            this.convertFloatModelToThree(this.get('tube'), 'tube'),
            this.get('tubularSegments'),
            this.get('radialSegments'),
            this.get('p'),
            this.get('q')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseGeometryModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['radius'] = 'convertFloat';
        this.property_converters['tube'] = 'convertFloat';
        this.property_converters['tubularSegments'] = null;
        this.property_converters['radialSegments'] = null;
        this.property_converters['p'] = null;
        this.property_converters['q'] = null;
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'TorusKnotGeometryModel',

    serializers: _.extend({
    },  BaseGeometryModel.serializers),
});

module.exports = {
    TorusKnotGeometryModel: TorusKnotGeometryModel,
};
