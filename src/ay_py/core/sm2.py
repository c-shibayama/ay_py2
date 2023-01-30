#!/usr/bin/python
#Simple new version of state machines.
import os,time
from util import *

class TStateMachine2(object):
  def __init__(self, states, start_state, debug=False):
    self.States= states
    self.StartState= start_state
    self.Debug= debug

  class TAction(object):
    def __init__(self):
      self.Entry= None
      self.Actions= []
      self.Else= None

  def LoadState(self, state):
    actions= self.TAction()
    for action in self.States[state]:
      if len(action)==0:  raise Exception('Invalid state description.')
      if action[0]=='entry':
        if len(action)!=2:  raise Exception('Invalid state description.')
        actions.Entry= action[1]  #Action
      elif action[0]=='else':
        if len(action)==2:  actions.Else= (action[1],None)  #Next state, no action
        elif len(action)==3:  actions.Else= (action[1],action[2])  #Next state, action
        else:  raise Exception('Invalid state description.')
      else:
        if len(action)==2:  actions.Actions.append((action[0],action[1],None))  #Condition, next state, no action
        elif len(action)==3:  actions.Actions.append((action[0],action[1],action[2]))  #Condition, next state, action
        else:  raise Exception('Invalid state description.')
    return actions

  def Run(self):
    self.prev_state= ''
    self.curr_state= self.StartState
    count= 0
    while self.curr_state!='':
      count+=1
      if self.Debug: CPrint(2, '@',count,self.curr_state)
      if self.curr_state not in self.States:
        raise Exception('State',self.curr_state,'does not exist.')
      actions= self.LoadState(self.curr_state)
      if actions.Entry and self.prev_state!=self.curr_state:
        if self.Debug: CPrint(2, '@',count,self.curr_state,'Entry')
        actions.Entry()

      a_id_satisfied= -1
      next_state= ''
      for a_id,(condition,next_st,action) in enumerate(actions.Actions):
        if condition():
          if a_id_satisfied>=0:
            print 'Warning: multiple conditions are satisfied in ',self.curr_state
            print '  First satisfied condition index, next state:',a_id_satisfied, next_state
            print '  Additionally satisfied condition index, next state:',a_id, next_st
            print '  First conditioned action is used'
          else:
            a_id_satisfied= a_id
            next_state= next_st

      #Execute action
      if a_id_satisfied>=0:
        if self.Debug: CPrint(2, '@',count,self.curr_state,'Condition satisfied:',a_id_satisfied)
        action= actions.Actions[a_id_satisfied][2]
        if action:
          if self.Debug: CPrint(2, '@',count,self.curr_state,'Action',a_id_satisfied)
          action()
      else:
        if actions.Else:
          next_st,action= actions.Else
          if action:
            if self.Debug: CPrint(2, '@',count,self.curr_state,'Else')
            action()
          next_state= next_st

      if self.Debug: CPrint(2, '@',count,self.curr_state,'Next state:',next_state)

      if next_state=='':
        raise Exception('Next state is not defined at',self.curr_state,'; Hint: use else action to specify the case where no conditions are satisfied.')
      elif next_state=='.exit':
        self.prev_state= self.curr_state
        self.curr_state= ''
      else:
        self.prev_state= self.curr_state
        self.curr_state= next_state
