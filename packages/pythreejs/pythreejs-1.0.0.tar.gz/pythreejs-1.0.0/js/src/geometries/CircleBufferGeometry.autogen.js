//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseBufferGeometryModel = require('../core/BaseBufferGeometry.autogen.js').BaseBufferGeometryModel;


var CircleBufferGeometryModel = BaseBufferGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseBufferGeometryModel.prototype.defaults.call(this), {

            radius: 1,
            segments: 8,
            thetaStart: 0,
            thetaLength: 6.283185307179586,
            type: "CircleBufferGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.CircleBufferGeometry(
            this.convertFloatModelToThree(this.get('radius'), 'radius'),
            this.get('segments'),
            this.convertFloatModelToThree(this.get('thetaStart'), 'thetaStart'),
            this.convertFloatModelToThree(this.get('thetaLength'), 'thetaLength')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseBufferGeometryModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['radius'] = 'convertFloat';
        this.property_converters['segments'] = null;
        this.property_converters['thetaStart'] = 'convertFloat';
        this.property_converters['thetaLength'] = 'convertFloat';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'CircleBufferGeometryModel',

    serializers: _.extend({
    },  BaseBufferGeometryModel.serializers),
});

module.exports = {
    CircleBufferGeometryModel: CircleBufferGeometryModel,
};
