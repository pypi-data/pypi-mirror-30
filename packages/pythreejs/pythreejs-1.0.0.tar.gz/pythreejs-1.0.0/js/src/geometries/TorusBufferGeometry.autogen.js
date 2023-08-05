//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseBufferGeometryModel = require('../core/BaseBufferGeometry.autogen.js').BaseBufferGeometryModel;


var TorusBufferGeometryModel = BaseBufferGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseBufferGeometryModel.prototype.defaults.call(this), {

            radius: 1,
            tube: 0.4,
            radialSegments: 8,
            tubularSegments: 6,
            arc: 6.283185307179586,
            type: "TorusBufferGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.TorusBufferGeometry(
            this.convertFloatModelToThree(this.get('radius'), 'radius'),
            this.convertFloatModelToThree(this.get('tube'), 'tube'),
            this.get('radialSegments'),
            this.get('tubularSegments'),
            this.convertFloatModelToThree(this.get('arc'), 'arc')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseBufferGeometryModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['radius'] = 'convertFloat';
        this.property_converters['tube'] = 'convertFloat';
        this.property_converters['radialSegments'] = null;
        this.property_converters['tubularSegments'] = null;
        this.property_converters['arc'] = 'convertFloat';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'TorusBufferGeometryModel',

    serializers: _.extend({
    },  BaseBufferGeometryModel.serializers),
});

module.exports = {
    TorusBufferGeometryModel: TorusBufferGeometryModel,
};
