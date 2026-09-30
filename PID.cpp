#include "PID.h"

PID::PID(){

}

PID::PID(float sampling_period, float proportional_gain, 
float integral_gain, float derivative_gain, 
float upper_saturation_limit, float lower_saturation_limit, 
float lowest_pwm_limit, float tau){
  this->sampling_period = sampling_period;
  this->proportional_gain = proportional_gain;
  this->integral_gain = integral_gain;
  this->derivative_gain = derivative_gain;
  intended_upper_saturation_limit = upper_saturation_limit;
  intended_lower_saturation_limit = lower_saturation_limit;
  this->upper_saturation_limit = upper_saturation_limit;
  this->lower_saturation_limit = lower_saturation_limit;
  this->lowest_pwm_limit = lowest_pwm_limit;
  this->tau = tau;

  integral = 0;
  previous_error = 0;
  previous_filtered_derivative_term = 0;
  error = 0;
}

float PID::control(float desired_speed, float current_speed, float uff){
  //calculate error
  error = desired_speed - current_speed;

  //calculate derivative
  float derivative = (error - previous_error) / sampling_period;

  //filter derivative
  float filtered_derivative_term = (tau/(tau + sampling_period))
  * previous_filtered_derivative_term
  + (sampling_period / (tau + sampling_period)) * derivative;

  //calculate proportional term
  float proportional_term = proportional_gain * error;

  //calculate integral term
  float previous_integral = integral;
  float integral_term = integral + (error * sampling_period * integral_gain);

  //calculate derivative term
  float derivative_term = filtered_derivative_term * derivative_gain;

  //Serial.print("Ts: ");
  //Serial.println(sampling_period);

  //Serial.print("Error: ");
  //Serial.println(error);

  //Serial.print("Derivative: ");
  //Serial.println(derivative);

  //Serial.print("Proportional Term: ");
  //Serial.print(proportional_term);
  //Serial.print("  Integral Term: ");
  //Serial.print(integral_term);
  //Serial.print("  Derivative Term: ");
  //Serial.println(derivative_term);

  //Anti overshoot
  if(error > 0 && previous_error < 0){
    integral_term = -previous_integral/8;
  }
  if(error < 0 && previous_error > 0){
    integral_term = -previous_integral/8;
  }

  //calculate complete PID output
  float output = proportional_term + integral_term + derivative_term + uff;

  //Anti-windup
  //only takes the new integral value if it would help
  if(output > upper_saturation_limit){
    output = upper_saturation_limit;
    if(error > 0){
      integral_term = previous_integral;
    }
  }
  else if(output < lower_saturation_limit){
    output = lower_saturation_limit;
    if(error < 0){
      integral_term = previous_integral;
    }
  }

  //update previous values
  previous_error = error;
  previous_filtered_derivative_term = filtered_derivative_term;
  integral = integral_term;

  //return controller output
  return output;
}

float PID::control_speed(float desired_speed, float current_speed, float uff){
  //calculate error
  error = desired_speed - current_speed;

  //calculate derivative
  float derivative = (error - previous_error) / sampling_period;

  //filter derivative
  float filtered_derivative_term = (tau/(tau + sampling_period))
  * previous_filtered_derivative_term
  + (sampling_period / (tau + sampling_period)) * derivative;

  //calculate proportional term
  float proportional_term = proportional_gain * error;

  //calculate integral term
  float previous_integral = integral;
  float integral_term = integral + (error * sampling_period * integral_gain);

  //calculate derivative term
  float derivative_term = filtered_derivative_term * derivative_gain;

  //Serial.print("Ts: ");
  //Serial.println(sampling_period);

  //Serial.print("Error: ");
  //Serial.println(error);

  //Serial.print("Derivative: ");
  //Serial.println(derivative);

  //Serial.print("Proportional Term: ");
  //Serial.print(proportional_term);
  //Serial.print("  Integral Term: ");
  //Serial.print(integral_term);
  //Serial.print("  Derivative Term: ");
  //Serial.println(derivative_term);

  //Anti overshoot
  if(error > 0 && previous_error < 0){
    integral_term = -previous_integral/16;
  }
  if(error < 0 && previous_error > 0){
    integral_term = -previous_integral/16;
  }

  //calculate complete PID output
  float output = proportional_term + integral_term + derivative_term + uff;

  if(output >= 0 && output < lowest_pwm_limit){
    output = lowest_pwm_limit;
  }
  else if(output < 0 && output > -lowest_pwm_limit){
    output = -lowest_pwm_limit;
  }

  //Anti-windup
  //only takes the new integral value if it would help
  if(output > upper_saturation_limit){
    output = upper_saturation_limit;
    if(error > 0){
      integral_term = previous_integral;
    }
  }
  else if(output < lower_saturation_limit){
    output = lower_saturation_limit;
    if(error < 0){
      integral_term = previous_integral;
    }
  }

  //update previous values
  previous_error = error;
  previous_filtered_derivative_term = filtered_derivative_term;
  integral = integral_term;

  //return controller output
  return output;
}

void PID::reset(){
  previous_error = 0;
  integral = 0;
  previous_filtered_derivative_term = 0;
}
