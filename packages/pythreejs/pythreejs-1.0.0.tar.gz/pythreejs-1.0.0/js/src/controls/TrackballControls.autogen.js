//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ControlsModel = require('./Controls.autogen.js').ControlsModel;


var TrackballControlsModel = ControlsModel.extend({

    defaults: function() {
        return _.extend(ControlsModel.prototype.defaults.call(this), {

            enabled: true,
            minDistance: 0,
            maxDistance: null,
            rotateSpeed: 1,
            zoomSpeed: 1.2,
            panSpeed: 0.3,
            staticMoving: false,
            dynamicDampingFactor: 0.2,
            noRotate: false,
            noZoom: false,
            noPan: false,
            noRoll: false,
            target: [0,0,0],

        });
    },

    constructThreeObject: function() {

        var result = new THREE.TrackballControls(
            this.convertThreeTypeModelToThree(this.get('controlling'), 'controlling')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ControlsModel.prototype.createPropertiesArrays.call(this);


        this.property_converters['enabled'] = 'convertBool';
        this.property_converters['minDistance'] = 'convertFloat';
        this.property_converters['maxDistance'] = 'convertFloat';
        this.property_converters['rotateSpeed'] = 'convertFloat';
        this.property_converters['zoomSpeed'] = 'convertFloat';
        this.property_converters['panSpeed'] = 'convertFloat';
        this.property_converters['staticMoving'] = 'convertBool';
        this.property_converters['dynamicDampingFactor'] = 'convertFloat';
        this.property_converters['noRotate'] = 'convertBool';
        this.property_converters['noZoom'] = 'convertBool';
        this.property_converters['noPan'] = 'convertBool';
        this.property_converters['noRoll'] = 'convertBool';
        this.property_converters['target'] = 'convertVector';

        this.property_assigners['target'] = 'assignVector';

    },

}, {

    model_name: 'TrackballControlsModel',

    serializers: _.extend({
    },  ControlsModel.serializers),
});

module.exports = {
    TrackballControlsModel: TrackballControlsModel,
};
