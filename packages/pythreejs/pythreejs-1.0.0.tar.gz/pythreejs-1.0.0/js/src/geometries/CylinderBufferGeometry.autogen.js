//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseBufferGeometryModel = require('../core/BaseBufferGeometry.autogen.js').BaseBufferGeometryModel;


var CylinderBufferGeometryModel = BaseBufferGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseBufferGeometryModel.prototype.defaults.call(this), {

            radiusTop: 1,
            radiusBottom: 1,
            height: 1,
            radiusSegments: 8,
            heightSegments: 1,
            openEnded: false,
            thetaStart: 0,
            thetaLength: 6.283185307179586,
            type: "CylinderBufferGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.CylinderBufferGeometry(
            this.convertFloatModelToThree(this.get('radiusTop'), 'radiusTop'),
            this.convertFloatModelToThree(this.get('radiusBottom'), 'radiusBottom'),
            this.convertFloatModelToThree(this.get('height'), 'height'),
            this.get('radiusSegments'),
            this.get('heightSegments'),
            this.convertBoolModelToThree(this.get('openEnded'), 'openEnded'),
            this.convertFloatModelToThree(this.get('thetaStart'), 'thetaStart'),
            this.convertFloatModelToThree(this.get('thetaLength'), 'thetaLength')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseBufferGeometryModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['radiusTop'] = 'convertFloat';
        this.property_converters['radiusBottom'] = 'convertFloat';
        this.property_converters['height'] = 'convertFloat';
        this.property_converters['radiusSegments'] = null;
        this.property_converters['heightSegments'] = null;
        this.property_converters['openEnded'] = 'convertBool';
        this.property_converters['thetaStart'] = 'convertFloat';
        this.property_converters['thetaLength'] = 'convertFloat';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'CylinderBufferGeometryModel',

    serializers: _.extend({
    },  BaseBufferGeometryModel.serializers),
});

module.exports = {
    CylinderBufferGeometryModel: CylinderBufferGeometryModel,
};
