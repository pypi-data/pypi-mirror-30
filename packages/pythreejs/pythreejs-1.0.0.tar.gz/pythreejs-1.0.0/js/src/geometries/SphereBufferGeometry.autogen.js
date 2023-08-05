//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseBufferGeometryModel = require('../core/BaseBufferGeometry.autogen.js').BaseBufferGeometryModel;


var SphereBufferGeometryModel = BaseBufferGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseBufferGeometryModel.prototype.defaults.call(this), {

            radius: 1,
            widthSegments: 8,
            heightSegments: 6,
            phiStart: 0,
            phiLength: 6.283185307179586,
            thetaStart: 0,
            thetaLength: 3.141592653589793,
            type: "SphereBufferGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.SphereBufferGeometry(
            this.convertFloatModelToThree(this.get('radius'), 'radius'),
            this.get('widthSegments'),
            this.get('heightSegments'),
            this.convertFloatModelToThree(this.get('phiStart'), 'phiStart'),
            this.convertFloatModelToThree(this.get('phiLength'), 'phiLength'),
            this.convertFloatModelToThree(this.get('thetaStart'), 'thetaStart'),
            this.convertFloatModelToThree(this.get('thetaLength'), 'thetaLength')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseBufferGeometryModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['radius'] = 'convertFloat';
        this.property_converters['widthSegments'] = null;
        this.property_converters['heightSegments'] = null;
        this.property_converters['phiStart'] = 'convertFloat';
        this.property_converters['phiLength'] = 'convertFloat';
        this.property_converters['thetaStart'] = 'convertFloat';
        this.property_converters['thetaLength'] = 'convertFloat';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'SphereBufferGeometryModel',

    serializers: _.extend({
    },  BaseBufferGeometryModel.serializers),
});

module.exports = {
    SphereBufferGeometryModel: SphereBufferGeometryModel,
};
