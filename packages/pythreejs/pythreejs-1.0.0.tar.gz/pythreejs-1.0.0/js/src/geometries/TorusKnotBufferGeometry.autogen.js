//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseBufferGeometryModel = require('../core/BaseBufferGeometry.autogen.js').BaseBufferGeometryModel;


var TorusKnotBufferGeometryModel = BaseBufferGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseBufferGeometryModel.prototype.defaults.call(this), {

            radius: 1,
            tube: 0.4,
            tubularSegments: 64,
            radialSegments: 8,
            p: 2,
            q: 3,
            type: "TorusKnotBufferGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.TorusKnotBufferGeometry(
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

        BaseBufferGeometryModel.prototype.createPropertiesArrays.call(this);

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

    model_name: 'TorusKnotBufferGeometryModel',

    serializers: _.extend({
    },  BaseBufferGeometryModel.serializers),
});

module.exports = {
    TorusKnotBufferGeometryModel: TorusKnotBufferGeometryModel,
};
