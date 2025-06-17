import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
import os
print("Dataset Directory Exists:", os.path.exists('Dataset'))
print("Subdirectories:", os.listdir('Dataset'))


# Load and preprocess data
datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

train_data = datagen.flow_from_directory('Dataset',
                                         target_size=(176, 176),
                                         batch_size=32,
                                         class_mode='categorical',
                                         subset='training')

val_data = datagen.flow_from_directory('Dataset',
                                       target_size=(176, 176),
                                       batch_size=32,
                                       class_mode='categorical',
                                       subset='validation')

# Define CNN Model
model = models.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(176, 176, 3)),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(4, activation='softmax')  # 4 classes
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Train the model
model.fit(train_data, validation_data=val_data, epochs=10)

# Create the models folder if it doesn't exist
if not os.path.exists('models'):
    os.makedirs('models')

# Save the model
model.save('models/model.h5')
print("Model saved at:", os.path.abspath('models/model.h5'))
