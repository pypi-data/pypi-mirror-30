//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseGeometryModel = require('../core/BaseGeometry.autogen.js').BaseGeometryModel;


var ConeGeometryModel = BaseGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseGeometryModel.prototype.defaults.call(this), {

            radius: 20,
            height: 100,
            radialSegments: 8,
            heightSegments: 1,
            openEnded: false,
            thetaStart: 0,
            thetaLength: 6.283185307179586,
            type: "ConeGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.ConeGeometry(
            this.convertFloatModelToThree(this.get('radius'), 'radius'),
            this.convertFloatModelToThree(this.get('height'), 'height'),
            this.get('radialSegments'),
            this.get('heightSegments'),
            this.convertBoolModelToThree(this.get('openEnded'), 'openEnded'),
            this.convertFloatModelToThree(this.get('thetaStart'), 'thetaStart'),
            this.convertFloatModelToThree(this.get('thetaLength'), 'thetaLength')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseGeometryModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['radius'] = 'convertFloat';
        this.property_converters['height'] = 'convertFloat';
        this.property_converters['radialSegments'] = null;
        this.property_converters['heightSegments'] = null;
        this.property_converters['openEnded'] = 'convertBool';
        this.property_converters['thetaStart'] = 'convertFloat';
        this.property_converters['thetaLength'] = 'convertFloat';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'ConeGeometryModel',

    serializers: _.extend({
    },  BaseGeometryModel.serializers),
});

module.exports = {
    ConeGeometryModel: ConeGeometryModel,
};
