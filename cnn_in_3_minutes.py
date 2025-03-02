# -*- coding: utf-8 -*-
"""CNN in 3 minutes.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1xpzsbU4LWGm2JmEdmmDFkNgW5SfW-1UB

#### Connect to google drive
"""

from google.colab import drive
drive.mount('/content/drive')

"""#### Import necessary libraries"""

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2
import os

"""#### Create training and validation dataset"""

train_dir = '/content/drive/MyDrive/CNN/dataset'
img_height, img_width = 150, 150
batch_size = 2

train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
    )

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='categorical',
    subset='training'
)

validation_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='categorical',
    subset='validation'
)

"""#### Define Architecture"""

from tensorflow.keras.metrics import Precision, Recall
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(img_height, img_width, 3)),
    BatchNormalization(),
    MaxPooling2D((2, 2)),

    Conv2D(64, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),

    Conv2D(128, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),

    Conv2D(256, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),

    Flatten(),

    Dense(512, activation='relu', kernel_regularizer=l2(0.001)),
    Dropout(0.5),
    Dense(4, activation='softmax')
])

model.compile(optimizer=Adam(learning_rate=0.0001),
              loss='categorical_crossentropy',
              metrics=['accuracy', Precision(), Recall()])

"""#### Train the model"""

epochs = 100

history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // batch_size,
    validation_data=validation_generator,
    validation_steps=validation_generator.samples // batch_size,
    epochs=epochs
)

"""#### Save Model"""

model.save('model.h5')

"""#### Evaluate Model"""

loss, accuracy, precision, recall = model.evaluate(validation_generator)
print("Loss:",loss)
print("Accuracy:",accuracy)
print("Precision:",precision)
print("Recall:",recall)

"""#### Make predictions"""

!ls /content/drive/MyDrive/CNN/not_to_train

from tensorflow.keras.preprocessing import image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

def predict_image(img_path):
    img = image.load_img(img_path, target_size=(img_height, img_width))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0

    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction, axis=1)
    class_labels = list(train_generator.class_indices.keys())
    return class_labels[predicted_class[0]]


directory = '/content/drive/MyDrive/CNN/not_to_train/'

files_and_dirs = os.listdir(directory)
files = [f for f in files_and_dirs if os.path.isfile(os.path.join(directory, f))]

for f in files:
  if f.endswith(".jpg"):
    result = predict_image(os.path.join(directory, f))
    print(f"The image is classified as: {result}")

    img = mpimg.imread(os.path.join(directory, f))  # Replace with your image path
    plt.imshow(img)
    plt.axis("off")  # Hide axes
    plt.show()

"""#### Transfer learning"""

from tensorflow.keras.applications import VGG16
from tensorflow.keras.layers import GlobalAveragePooling2D

base_model = VGG16(weights='imagenet', include_top=False, input_shape=(img_height, img_width, 3))
base_model.trainable = False

model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dense(1024, activation='relu'),
    Dense(4, activation='softmax')
])
from tensorflow.keras.metrics import Precision, Recall

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy', Precision(), Recall()])

epochs = 100

history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // batch_size,
    validation_data=validation_generator,
    validation_steps=validation_generator.samples // batch_size,
    epochs=epochs
)

loss, accuracy, precision, recall = model.evaluate(validation_generator)
print("Loss:",loss)
print("Accuracy:",accuracy)
print("Precision:",precision)
print("Recall:",recall)

"""#### Confusion Matrix"""

from sklearn.metrics import confusion_matrix
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt


test_datagen = ImageDataGenerator(rescale=1./255)
test_generator = test_datagen.flow_from_directory(
    '/content/drive/MyDrive/CNN/dataset',
    target_size=(img_height, img_width),
    batch_size=32,
    class_mode='categorical',
    shuffle=False
)
true_labels = test_generator.classes
predictions = model.predict(test_generator)
predicted_labels = np.argmax(predictions, axis=1)

cm = confusion_matrix(true_labels, predicted_labels)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=test_generator.class_indices.keys(), yticklabels=test_generator.class_indices.keys())
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix')
plt.show()

