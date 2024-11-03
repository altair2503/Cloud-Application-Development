# train.py
import tensorflow as tf
import numpy as np

def train():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(10, activation='relu', input_shape=(3,)),
        tf.keras.layers.Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse')

    x_train = np.random.rand(100, 3)
    y_train = np.random.rand(100, 1)

    model.fit(x_train, y_train, epochs=5)

    # Save the model in the new .keras format
    model.save('local_model.keras')
    print("Model trained and saved as 'local_model.keras'")

if __name__ == '__main__':
    train()