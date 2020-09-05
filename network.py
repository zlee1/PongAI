from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras.utils.np_utils import to_categorical

from pong import RunGame
import sys
import numpy as np

from random import randint

total_games = 10000
num_games = 0

x_train = np.array([])
y_train = np.array([])

train_frequency = 1

model = Sequential()
model.add(Dense(1, input_dim=1, activation='sigmoid'))
model.add(Dense(2, activation='softmax'))
model.compile(Adam(lr=0.1), loss='categorical_crossentropy', metrics=['accuracy'])

last_distance = None

class Wrapper(object):
    def __init__(self):
        game = RunGame()
        game.controlled_run(self, num_games)
        
    def control(self, values):
        global x_train
        global y_train
        global highest_score
        
        global model
        
        global last_distance
        
        if num_games < 5:
            if last_distance == None:
                last_distance = values['paddle_position'] - values['ball_end_y']
                
            if abs(last_distance) > abs(values['paddle_position'] - values['ball_end_y']) and x_train.size < 1000:
                if values['last_action'] != None:
                    x_train = np.append(x_train, values['paddle_position'] - values['ball_end_y'])
                    y_train = np.append(y_train, values['last_action'])
            
            last_distance = values['paddle_position'] - values['ball_end_y']
        
        prediction = model.predict_classes(np.array([[values['paddle_position'] - values['ball_end_y']]]))

        r = randint(0, 3)
        
        random_rate = 1*(1-(num_games)/1)
        
        if r <= random_rate:
            if prediction == 0:
                return 1
            else:
                return 0
        else:
            if prediction == 1:
                return 1
            else:
                return 0
        
    def gameover(self, score):
        global num_games
        global x_train
        global y_train
        global model
        
        num_games += 1
        
        if num_games % train_frequency == 0:
            if x_train.size > 0 and y_train.size > 0:
                y_train_cat = to_categorical(y_train, 2)
                model.fit(x_train, y_train_cat, epochs = 50, verbose = 1, shuffle = 1)
                #x_train = np.array([])
                #y_train = np.array([])
            
            
        
        if num_games >= total_games:
            sys.exit()
        game = RunGame()
        game.controlled_run(self, num_games)

if __name__ == '__main__':
    w = Wrapper()
