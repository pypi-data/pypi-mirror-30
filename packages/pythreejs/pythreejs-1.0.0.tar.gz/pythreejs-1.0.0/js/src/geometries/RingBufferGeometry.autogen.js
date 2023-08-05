//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseBufferGeometryModel = require('../core/BaseBufferGeometry.autogen.js').BaseBufferGeometryModel;


var RingBufferGeometryModel = BaseBufferGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseBufferGeometryModel.prototype.defaults.call(this), {

            innerRadius: 0.5,
            outerRadius: 1,
            thetaSegments: 8,
            phiSegments: 8,
            thetaStart: 0,
            thetaLength: 6.283185307179586,
            type: "RingBufferGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.RingBufferGeometry(
            this.convertFloatModelToThree(this.get('innerRadius'), 'innerRadius'),
            this.convertFloatModelToThree(this.get('outerRadius'), 'outerRadius'),
            this.get('thetaSegments'),
            this.get('phiSegments'),
            this.convertFloatModelToThree(this.get('thetaStart'), 'thetaStart'),
            this.convertFloatModelToThree(this.get('thetaLength'), 'thetaLength')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseBufferGeometryModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['innerRadius'] = 'convertFloat';
        this.property_converters['outerRadius'] = 'convertFloat';
        this.property_converters['thetaSegments'] = null;
        this.property_converters['phiSegments'] = null;
        this.property_converters['thetaStart'] = 'convertFloat';
        this.property_converters['thetaLength'] = 'convertFloat';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'RingBufferGeometryModel',

    serializers: _.extend({
    },  BaseBufferGeometryModel.serializers),
});

module.exports = {
    RingBufferGeometryModel: RingBufferGeometryModel,
};
