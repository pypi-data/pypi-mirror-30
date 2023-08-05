//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;


var RayModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            origin: [0,0,0],
            direction: [0,0,0],

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Ray(
            this.convertVectorModelToThree(this.get('origin'), 'origin'),
            this.convertVectorModelToThree(this.get('direction'), 'direction')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);


        this.property_converters['origin'] = 'convertVector';
        this.property_converters['direction'] = 'convertVector';

        this.property_assigners['origin'] = 'assignVector';
        this.property_assigners['direction'] = 'assignVector';

    },

}, {

    model_name: 'RayModel',

    serializers: _.extend({
    },  ThreeModel.serializers),
});

module.exports = {
    RayModel: RayModel,
};
