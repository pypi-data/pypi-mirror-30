//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseGeometryModel = require('../core/BaseGeometry.autogen.js').BaseGeometryModel;


var RingGeometryModel = BaseGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseGeometryModel.prototype.defaults.call(this), {

            innerRadius: 0.5,
            outerRadius: 1,
            thetaSegments: 8,
            phiSegments: 8,
            thetaStart: 0,
            thetaLength: 6.283185307179586,
            type: "RingGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.RingGeometry(
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

        BaseGeometryModel.prototype.createPropertiesArrays.call(this);

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

    model_name: 'RingGeometryModel',

    serializers: _.extend({
    },  BaseGeometryModel.serializers),
});

module.exports = {
    RingGeometryModel: RingGeometryModel,
};
