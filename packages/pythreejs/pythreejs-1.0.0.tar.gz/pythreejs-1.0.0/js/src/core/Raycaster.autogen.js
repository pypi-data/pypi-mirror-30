//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;

var RayModel = require('../math/Ray.autogen.js').RayModel;

var RaycasterModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            origin: [0,0,0],
            direction: [0,0,0],
            near: 0,
            far: 1000000,
            ray: null,
            linePrecision: 1,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Raycaster(
            this.convertVectorModelToThree(this.get('origin'), 'origin'),
            this.convertVectorModelToThree(this.get('direction'), 'direction'),
            this.convertFloatModelToThree(this.get('near'), 'near'),
            this.convertFloatModelToThree(this.get('far'), 'far')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('ray');


        this.property_converters['origin'] = 'convertVector';
        this.property_converters['direction'] = 'convertVector';
        this.property_converters['near'] = 'convertFloat';
        this.property_converters['far'] = 'convertFloat';
        this.property_converters['ray'] = 'convertThreeType';
        this.property_converters['linePrecision'] = 'convertFloat';

        this.property_assigners['origin'] = 'assignVector';
        this.property_assigners['direction'] = 'assignVector';

    },

}, {

    model_name: 'RaycasterModel',

    serializers: _.extend({
        ray: { deserialize: widgets.unpack_models },
    },  ThreeModel.serializers),
});

module.exports = {
    RaycasterModel: RaycasterModel,
};
