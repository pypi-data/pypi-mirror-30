//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;

var PlaneModel = require('./Plane.autogen.js').PlaneModel;

var FrustumModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            p0: null,
            p1: null,
            p2: null,
            p3: null,
            p4: null,
            p5: null,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Frustum(
            this.convertThreeTypeModelToThree(this.get('p0'), 'p0'),
            this.convertThreeTypeModelToThree(this.get('p1'), 'p1'),
            this.convertThreeTypeModelToThree(this.get('p2'), 'p2'),
            this.convertThreeTypeModelToThree(this.get('p3'), 'p3'),
            this.convertThreeTypeModelToThree(this.get('p4'), 'p4'),
            this.convertThreeTypeModelToThree(this.get('p5'), 'p5')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('p0');
        this.three_properties.push('p1');
        this.three_properties.push('p2');
        this.three_properties.push('p3');
        this.three_properties.push('p4');
        this.three_properties.push('p5');


        this.property_converters['p0'] = 'convertThreeType';
        this.property_converters['p1'] = 'convertThreeType';
        this.property_converters['p2'] = 'convertThreeType';
        this.property_converters['p3'] = 'convertThreeType';
        this.property_converters['p4'] = 'convertThreeType';
        this.property_converters['p5'] = 'convertThreeType';


    },

}, {

    model_name: 'FrustumModel',

    serializers: _.extend({
        p0: { deserialize: widgets.unpack_models },
        p1: { deserialize: widgets.unpack_models },
        p2: { deserialize: widgets.unpack_models },
        p3: { deserialize: widgets.unpack_models },
        p4: { deserialize: widgets.unpack_models },
        p5: { deserialize: widgets.unpack_models },
    },  ThreeModel.serializers),
});

module.exports = {
    FrustumModel: FrustumModel,
};
