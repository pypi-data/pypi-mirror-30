//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;


var QuaternionModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            x: 0,
            y: 0,
            z: 0,
            w: 1,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Quaternion(
            this.convertFloatModelToThree(this.get('x'), 'x'),
            this.convertFloatModelToThree(this.get('y'), 'y'),
            this.convertFloatModelToThree(this.get('z'), 'z'),
            this.convertFloatModelToThree(this.get('w'), 'w')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);


        this.property_converters['x'] = 'convertFloat';
        this.property_converters['y'] = 'convertFloat';
        this.property_converters['z'] = 'convertFloat';
        this.property_converters['w'] = 'convertFloat';


    },

}, {

    model_name: 'QuaternionModel',

    serializers: _.extend({
    },  ThreeModel.serializers),
});

module.exports = {
    QuaternionModel: QuaternionModel,
};
