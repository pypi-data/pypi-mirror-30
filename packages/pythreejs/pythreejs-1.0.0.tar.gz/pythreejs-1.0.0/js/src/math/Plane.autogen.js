//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;


var PlaneModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            normal: [0,0,0],
            constant: 0,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Plane(
            this.convertVectorModelToThree(this.get('normal'), 'normal'),
            this.convertFloatModelToThree(this.get('constant'), 'constant')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);


        this.property_converters['normal'] = 'convertVector';
        this.property_converters['constant'] = 'convertFloat';

        this.property_assigners['normal'] = 'assignVector';

    },

}, {

    model_name: 'PlaneModel',

    serializers: _.extend({
    },  ThreeModel.serializers),
});

module.exports = {
    PlaneModel: PlaneModel,
};
