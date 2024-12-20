from fastapi import WebSocket, FastAPI, status, Query, HTTPException
from typing import Annotated
import time
from abc import ABC, abstractmethod
import json
import random

class Game(ABC):
    def __init__(self, name: str, num_players: int) -> None:
        self.name = name
        self.num_players = num_players
    @abstractmethod
    def createGame():
        pass

# random assortment of characters 
class Testing(Game):
    characters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    def __init__(self):
        super().__init__("Guess Number of Characters in Stream", 2)
        self._player_name: str = ""
        self.userGuesses: list[int] = []
        self.character_to_guess: str = ""
        self.answer: int = 0
    def createGame(self, name: str) -> str:
        if not name:
            return { 'message': "Sorry, please input a valid name", 'success': False }
        self.player_name = name
        
        return { 'message': f"Welcome {self.player_name} to 'Guess the Number of Characters!'", 'success': True }
    
    def generateCharacters(self):
        rand_characters = []
        specific_char_to_guess = random.randint(0, len(Testing.characters)-1)
        self.character_to_guess = Testing.characters[specific_char_to_guess]
        length_of_arr = random.randint(5, 10)
        for _ in range(length_of_arr):
            ind = random.randint(0, len(Testing.characters)-1)
            if ind == specific_char_to_guess:
                self.answer+=1
            rand_characters.append(Testing.characters[ind])
        
        return rand_characters
    
    # @property
    def player_name(self):
        return self.player_name
    
    # @player_name.setter
    # def player_name(self, name):
    #     self.player_name = name
    
    # @property
    def get_character_to_guess(self):
        return self.character_to_guess
    
    # @character_to_guess.setter
    # def character_to_guess(self, character):
    #     self.character_to_guess = character
    # @property
    def num_guesses(self):
        return len(self.userGuesses)
    
    # @property
    def get_answer(self) -> int:
        return self.answer
    
    # @answer.setter
    # def answer(self, answer):
    #     self.answer = answer
    
    def addPlayerAnswer(self, answer: int):
        self.userGuesses.append(answer)
    
    def resetGame(self):
        self.userGuesses = []
        self.answer = 0
        
        

app = FastAPI()

game = None

@app.get('/createGame', status_code=status.HTTP_200_OK)
def setGame(name: Annotated[str | None, Query()] = None):
    try:
        global game
        game = Testing()
        message = game.createGame(name=name)
        if not message['success']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message['message'])
        return {
            'message': message['message']
        }
        
    except HTTPException as e:
        raise HTTPException(
            e.status_code,
            e.detail
        )

@app.websocket("/play")
async def playGame(websocket: WebSocket):
    try:
        await websocket.accept()
        if not game.player_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No player name found, please set up the game first")
        await websocket.send_text("Please respond with the number of a specific character there is in below 5 seconds")
        while True:
            """Game mechanics go here"""
            characters = game.generateCharacters()
            await websocket.send_text(f"The character you're looking for is '{game.character_to_guess}'.\nHere's the list of characters:\n{json.dumps(characters)}.")
            start_time = time.time()
            user_response = await websocket.receive_text()
            game.addPlayerAnswer(int(user_response))
            end_time = time.time()
            if start_time - end_time > 10:
                user_response = await websocket.send_text("Oh, you didn't answer in time. Would you like to try again?\n1 for Yes and 0 for No")
                if not int(user_response):
                    break
            elif int(user_response) == game.get_answer():
                await websocket.send_text(f"Congratulations, you guessed it correctly! It took you {game.num_guesses()}. Would you like to play again?\n1 for Yes and 0 for No")
                user_response = await websocket.receive_text()
                if not int(user_response):
                    break
            else:
                await websocket.send_text(f"You just missed the correct number of for the character: {game.num_guesses()}. Would you like to try again?\n1 for Yes and 0 for No")
                user_response = await websocket.receive_text()
                if not int(user_response):
                    break
            game.resetGame()

        """After user finishes guessing, need to have an input to play again"""
        await websocket.close()
    except HTTPException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )
        
    
    
    


    

        
        
        
        