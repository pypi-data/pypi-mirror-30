from keras.models import Sequential

def _get_relevant_params(dict_obj):
    relevant_params = ['batch_size',
                        'epochs',
                        'initial_epoch',
                        'loss',
                        'loss_weights',
                        'metrics',
                        'metrics_names',
                        'optimizer',
                        'shuffle',
                        'steps_per_epoch',
                        'stop_training',
                        'supports_masking',
                        'validation_split',
                        'validation_steps',
                        'weighted_metrics']
    result = {}

    #Extact the relevant link
    for rp in relevant_params:
        try:
            result[rp] = dict_obj[rp]
            if rp == 'optimizer':
                result[rp] = result[rp].__class__.__name__
        except KeyError:
            pass

    return result

def _get_layer_info(layers):
    result = []
    for layer in layers:
        layer_name = "%s (%s)" %  (layer.name, layer.__class__.__name__)
        output_shape = str(layer.output_shape)
        params = layer.count_params()
        tag =   layer.tag if layer.tag else ''

        result.append([layer_name, output_shape, params, tag])

    return result

class Sequential(Sequential):

    def fit_generator(self,
                      generator,
                      steps_per_epoch=None,
                      epochs=1,
                      verbose=1,
                      callbacks=None,
                      validation_data=None,
                      validation_steps=None,
                      class_weight=None,
                      max_queue_size=10,
                      workers=1,
                      use_multiprocessing=False,
                      shuffle=True,
                      initial_epoch=0):
        self.steps_per_epoch=steps_per_epoch
        self.epochs=epochs
        self.verbose=verbose
        self.callbacks=callbacks
        self.validation_steps=validation_steps
        self.max_queue_size=max_queue_size
        self.workers=workers
        self.use_multiprocessing=use_multiprocessing
        self.shuffle=shuffle
        self.initial_epoch=initial_epoch

        return super(Sequential, self).fit_generator(generator,
                steps_per_epoch,
                epochs,
                verbose,
                callbacks,
                validation_data,
                validation_steps,
                class_weight,
                max_queue_size,
                workers,
                use_multiprocessing,
                shuffle,
                initial_epoch)

    def fit(self,
            x=None,
            y=None,
            batch_size=None,
            epochs=1,
            verbose=1,
            callbacks=None,
            validation_split=0.,
            validation_data=None,
            shuffle=True,
            class_weight=None,
            sample_weight=None,
            initial_epoch=0,
            steps_per_epoch=None,
            validation_steps=None,
            **kwargs):
        self.batch_size=batch_size
        self.epochs=epochs
        self.verbose=verbose
        self.validation_split=validation_split
        self.shuffle=shuffle
        self.initial_epoch=initial_epoch
        self.steps_per_epoch=steps_per_epoch
        self.validation_steps=validation_steps

        return super(Sequential, self).fit(x,
                y,
                batch_size,
                epochs,
                verbose,
                callbacks,
                validation_split,
                validation_data,
                shuffle,
                class_weight,
                sample_weight,
                initial_epoch,
                steps_per_epoch,
                validation_steps,
                **kwargs)
