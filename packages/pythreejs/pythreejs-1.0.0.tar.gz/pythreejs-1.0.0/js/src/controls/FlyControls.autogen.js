//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ControlsModel = require('./Controls.autogen.js').ControlsModel;


var FlyControlsModel = ControlsModel.extend({

    defaults: function() {
        return _.extend(ControlsModel.prototype.defaults.call(this), {

            moveVector: [0,0,0],
            rotationVector: [0,0,0],
            movementSpeed: 1,
            rollSpeed: 0.05,
            syncRate: 1,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.FlyControls(
            this.convertThreeTypeModelToThree(this.get('controlling'), 'controlling')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ControlsModel.prototype.createPropertiesArrays.call(this);


        this.property_converters['moveVector'] = 'convertVector';
        this.property_converters['rotationVector'] = 'convertVector';
        this.property_converters['movementSpeed'] = 'convertFloat';
        this.property_converters['rollSpeed'] = 'convertFloat';
        this.property_converters['syncRate'] = 'convertFloat';

        this.property_assigners['moveVector'] = 'assignVector';
        this.property_assigners['rotationVector'] = 'assignVector';

    },

}, {

    model_name: 'FlyControlsModel',

    serializers: _.extend({
    },  ControlsModel.serializers),
});

module.exports = {
    FlyControlsModel: FlyControlsModel,
};
