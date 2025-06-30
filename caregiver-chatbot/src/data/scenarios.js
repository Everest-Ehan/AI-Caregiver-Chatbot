export const scenarios = {
  no_schedule: {
    id: 'no_schedule',
    name: 'No Schedule on Calendar',
    description: 'Caregiver clocked in but no schedule appears on calendar',
    contextFields: {
      client_name: {
        label: 'Client Name',
        placeholder: 'Enter client name',
        required: true
      },
      caregiver_name: {
        label: 'Caregiver Name',
        placeholder: 'Enter caregiver name',
        required: true
      },
      regular_schedule: {
        label: 'Regular Schedule',
        placeholder: 'e.g., Mon-Fri 9am-5pm',
        required: false
      },
      office_location: {
        label: 'Office Location',
        placeholder: 'e.g., New York, California',
        required: true
      }
    },
    steps: [
      {
        id: 'greeting',
        agent: 'Hello, this is Rosella, I am calling from Independence Care, how are you doing today?',
        expectedResponses: ['greeting_response'],
        nextStep: 'confirm_client'
      },
      {
        id: 'confirm_client',
        agent: 'I see you clocked in but there seems to be no schedule on your Calendar, can you confirm the client you are working with today?',
        expectedResponses: ['client_confirmation'],
        nextStep: 'check_regular_schedule'
      },
      {
        id: 'check_regular_schedule',
        agent: 'Thank you for confirming, Is this your regular schedule?',
        expectedResponses: ['yes', 'no'],
        nextStep: 'handle_schedule_type'
      },
      {
        id: 'handle_schedule_type',
        agent: 'You will have to remove one of your visits from the schedule this week, would you like to remove Wednesday or Friday?',
        expectedResponses: ['wednesday', 'friday'],
        nextStep: 'client_confirmation_call'
      },
      {
        id: 'client_confirmation_call',
        agent: 'Okay, no problem. Can you just bring the client to the phone, so I can confirm the change with him?',
        expectedResponses: ['client_available'],
        nextStep: 'client_verification'
      },
      {
        id: 'client_verification',
        agent: 'Hi, can you state your name for me?',
        expectedResponses: ['client_name'],
        nextStep: 'schedule_confirmation_with_client'
      },
      {
        id: 'schedule_confirmation_with_client',
        agent: 'Okay wonderful, Mr.{client_name} because your aide came today, we will need to adjust your schedule so that you do not over service your authorization. Can you confirm that the Caregiver can swap any other day of the week for today?',
        expectedResponses: ['yes', 'no'],
        nextStep: 'final_confirmation'
      },
      {
        id: 'final_confirmation',
        agent: 'Great, your caregiver will be with you today and will no longer be scheduled Friday from 9am to 5pm. Can I help you with anything else?',
        expectedResponses: ['yes', 'no'],
        nextStep: 'goodbye'
      },
      {
        id: 'goodbye',
        agent: 'Okay, have a great day!',
        expectedResponses: [],
        nextStep: null
      }
    ]
  },
  
  out_of_window: {
    id: 'out_of_window',
    name: 'Out of Window (Late Clock In)',
    description: 'Caregiver clocked in late for their shift',
    contextFields: {
      client_name: {
        label: 'Client Name',
        placeholder: 'Enter client name',
        required: true
      },
      caregiver_name: {
        label: 'Caregiver Name',
        placeholder: 'Enter caregiver name',
        required: true
      },
      scheduled_start_time: {
        label: 'Scheduled Start Time',
        placeholder: 'e.g., 9:00 AM',
        required: true
      },
      actual_start_time: {
        label: 'Actual Start Time',
        placeholder: 'e.g., 9:05 AM',
        required: true
      },
      shift_duration: {
        label: 'Shift Duration (hours)',
        placeholder: 'e.g., 8',
        required: true
      },
      office_location: {
        label: 'Office Location',
        placeholder: 'e.g., New York, California',
        required: true
      },
      late_reason: {
        label: 'Reason for Being Late',
        placeholder: 'e.g., Forgot to clock in, Doctor appointment',
        required: false
      }
    },
    steps: [
      {
        id: 'greeting',
        agent: 'Hello, this is Rosella, I am calling from Independence Care, how are you doing today!',
        expectedResponses: ['greeting_response'],
        nextStep: 'late_notice'
      },
      {
        id: 'late_notice',
        agent: 'I have noticed that you clocked in late for your shift today, I just wanted to confirm what was the reason for that?',
        expectedResponses: ['forgot_clock_in', 'actually_late'],
        nextStep: 'handle_late_reason'
      },
      {
        id: 'handle_late_reason',
        agent: 'Ohh! I totally understand, can you tell me what time you are coming today?',
        expectedResponses: ['time_response'],
        nextStep: 'client_verification_late'
      },
      {
        id: 'client_verification_late',
        agent: 'Thats great, can you also put the client on the phone so we can confirm with them?',
        expectedResponses: ['client_available'],
        nextStep: 'client_time_confirmation'
      },
      {
        id: 'client_time_confirmation',
        agent: 'Hi, can you state your name?',
        expectedResponses: ['client_name'],
        nextStep: 'client_arrival_time'
      },
      {
        id: 'client_arrival_time',
        agent: 'Great, can you confirm what time your aide showed up today?',
        expectedResponses: ['arrival_time'],
        nextStep: 'schedule_adjustment'
      },
      {
        id: 'schedule_adjustment',
        agent: 'Great, thank you. We will adjust the schedule for a start time of {adjusted_time}. We will adjust the scheduled clock out time for {adjusted_end_time}, so you do not lose any hours today. Can you put your aide back on the phone please?',
        expectedResponses: ['caregiver_back'],
        nextStep: 'final_adjustment_notice'
      },
      {
        id: 'final_adjustment_notice',
        agent: 'Hi, so the client confirmed you showed up at {adjusted_time} so your schedule has been adjusted to reflect that arrival time. Moving forward, I want to let you know that we are not allowed to make any changes to any clock in or clock out time. So, going forward please make sure you are very careful with your clock in and clock out because we will not be able to adjust them due to {office_location} state law.',
        expectedResponses: ['acknowledgment'],
        nextStep: 'goodbye_late'
      },
      {
        id: 'goodbye_late',
        agent: 'Thank you, have a good day!',
        expectedResponses: [],
        nextStep: null
      }
    ]
  },
  
  gps_out_of_range: {
    id: 'gps_out_of_range',
    name: 'GPS Signal Out of Range',
    description: 'Caregiver clocked in outside client\'s service area',
    contextFields: {
      client_name: {
        label: 'Client Name',
        placeholder: 'Enter client name',
        required: true
      },
      caregiver_name: {
        label: 'Caregiver Name',
        placeholder: 'Enter caregiver name',
        required: true
      },
      client_address: {
        label: 'Client Address',
        placeholder: 'Enter client\'s home address',
        required: true
      },
      clock_in_location: {
        label: 'Clock In Location',
        placeholder: 'Where did caregiver clock in?',
        required: true
      },
      office_state: {
        label: 'Office State',
        placeholder: 'e.g., NY, CA, TX',
        required: true
      },
      errand_details: {
        label: 'Errand Details (if applicable)',
        placeholder: 'What was picked up for client?',
        required: false
      }
    },
    steps: [
      {
        id: 'greeting',
        agent: 'Hello, this is Rosella, I am calling from Independence Care, how are you doing today!',
        expectedResponses: ['greeting_response'],
        nextStep: 'gps_notice'
      },
      {
        id: 'gps_notice',
        agent: 'I have noticed you have clocked in outside of the client\'s service area, which is not close to your client\'s house. Can you please clock in again once you are at your client\'s house, because we are not able to accept this clock in.',
        expectedResponses: ['app_fault', 'errand_for_client'],
        nextStep: 'handle_gps_issue'
      },
      {
        id: 'handle_gps_issue',
        agent: 'I am sorry to hear that but it can\'t be the applications fault because all of our CG\'s are using the same application and this does not seem to be the issues with anyone else at the moment, but can you try to clock in again and make sure are you inside your client\'s house.',
        expectedResponses: ['will_try', 'cant_clock_in'],
        nextStep: 'unscheduled_visit_suggestion'
      },
      {
        id: 'unscheduled_visit_suggestion',
        agent: 'Ohh! Okay there should be an option in your app called unscheduled visit\'s try doing it from there and see it if lets you!',
        expectedResponses: ['will_try'],
        nextStep: 'gps_goodbye'
      },
      {
        id: 'gps_goodbye',
        agent: 'Thank you, please feel free to reach us if you come across any problems. Remember it is {office_state} law that a Home Care agency cannot bill for visits that are rendered outside of the client\'s home.',
        expectedResponses: [],
        nextStep: null
      }
    ]
  },
  
  wrong_phone: {
    id: 'wrong_phone',
    name: 'Call From Caregiver Number',
    description: 'Caregiver used IVR number from their phone instead of client\'s house phone',
    contextFields: {
      client_name: {
        label: 'Client Name',
        placeholder: 'Enter client name',
        required: true
      },
      caregiver_name: {
        label: 'Caregiver Name',
        placeholder: 'Enter caregiver name',
        required: true
      },
      client_phone: {
        label: 'Client\'s House Phone',
        placeholder: 'Enter client\'s house phone number',
        required: true
      },
      caregiver_phone: {
        label: 'Caregiver\'s Phone',
        placeholder: 'Enter caregiver\'s phone number',
        required: true
      },
      ivr_number: {
        label: 'IVR Number Used',
        placeholder: 'Enter the IVR number that was called',
        required: true
      }
    },
    steps: [
      {
        id: 'greeting',
        agent: 'Hello, this is Rosella, I am calling from Independence Care, how are you doing today!',
        expectedResponses: ['greeting_response'],
        nextStep: 'wrong_phone_notice'
      },
      {
        id: 'wrong_phone_notice',
        agent: 'I have noticed that you used the IVR number to clock in today, but you used your phone to call that number instead of the client\'s house phone. Can you please clock in again using the client\'s house phone?',
        expectedResponses: ['will_do', 'client_wont_allow'],
        nextStep: 'handle_phone_issue'
      },
      {
        id: 'handle_phone_issue',
        agent: 'Thats unfortunate, in this situation I would recommend you use the HHA app to clock in.',
        expectedResponses: ['app_issue'],
        nextStep: 'coordinator_help'
      },
      {
        id: 'coordinator_help',
        agent: 'Okay, for that I can have one of our care coordinator\'s give you a call and get your HHA app set up. Does that sound good to you?',
        expectedResponses: ['yes', 'no'],
        nextStep: 'phone_goodbye'
      },
      {
        id: 'phone_goodbye',
        agent: 'Great! I will rely on this message to them, and someone will contact you shortly, is there anything else I can assist you with today?',
        expectedResponses: ['yes', 'no'],
        nextStep: 'final_goodbye'
      },
      {
        id: 'final_goodbye',
        agent: 'Okay, then you have a good day ahead. Take care, bye!',
        expectedResponses: [],
        nextStep: null
      }
    ]
  },
  
  phone_not_found: {
    id: 'phone_not_found',
    name: 'Phone Number Not Found',
    description: 'Caregiver used unregistered phone number',
    contextFields: {
      client_name: {
        label: 'Client Name',
        placeholder: 'Enter client name',
        required: true
      },
      caregiver_name: {
        label: 'Caregiver Name',
        placeholder: 'Enter caregiver name',
        required: true
      },
      new_phone_number: {
        label: 'New Phone Number',
        placeholder: 'Enter the new phone number used',
        required: true
      },
      old_phone_number: {
        label: 'Previous Phone Number',
        placeholder: 'Enter the previous registered phone number',
        required: false
      },
      phone_owner: {
        label: 'Phone Owner',
        placeholder: 'Who owns this phone number?',
        required: true
      }
    },
    steps: [
      {
        id: 'greeting',
        agent: 'Hello, this is Rosella, I am calling from Independence Care, how are you doing today!',
        expectedResponses: ['greeting_response'],
        nextStep: 'phone_number_notice'
      },
      {
        id: 'phone_number_notice',
        agent: 'I have noticed that you have clocked in using a phone number that is not registered with us. Can you confirm whose number this is? ({phone_number})',
        expectedResponses: ['client_new_number'],
        nextStep: 'client_verification_phone'
      },
      {
        id: 'client_verification_phone',
        agent: 'Okay, can your client confirm that?',
        expectedResponses: ['client_available'],
        nextStep: 'client_phone_verification'
      },
      {
        id: 'client_phone_verification',
        agent: 'Hello, this is Rosella from Independence Care, how are you doing today?',
        expectedResponses: ['client_greeting'],
        nextStep: 'client_identity'
      },
      {
        id: 'client_identity',
        agent: 'That\'s great to hear. Can you please confirm who I am talking to?',
        expectedResponses: ['client_name'],
        nextStep: 'phone_number_confirmation'
      },
      {
        id: 'phone_number_confirmation',
        agent: 'Perfect! I just wanted to confirm if this is your new phone ({phone_number})',
        expectedResponses: ['yes', 'no'],
        nextStep: 'future_usage'
      },
      {
        id: 'future_usage',
        agent: 'Great and will this be the number your caregiver will be using to clock in going forward?',
        expectedResponses: ['yes', 'no'],
        nextStep: 'phone_update_goodbye'
      },
      {
        id: 'phone_update_goodbye',
        agent: 'Sounds great! Then I will make sure this gets updated in your profile. Thank you for your time. You guys have a good day.',
        expectedResponses: [],
        nextStep: null
      }
    ]
  }
};

export const responseMappings = {
  greeting_response: ['i am doing well', 'i am doing good', 'i am doing okay', 'hi', 'hello'],
  client_confirmation: ['john doe', 'client name', 'working with'],
  yes: ['yes', 'yeah', 'sure', 'okay', 'fine'],
  no: ['no', 'nope', 'not really'],
  wednesday: ['wednesday', 'wed'],
  friday: ['friday', 'fri'],
  client_available: ['sure', 'okay', 'here they are', 'client available'],
  client_name: ['john', 'doe', 'client name'],
  forgot_clock_in: ['forgot to clock in', 'forgot clock in', 'was here on time'],
  actually_late: ['came in late', 'was late', 'late today'],
  time_response: ['9am', '9 am', 'nine', 'nine am'],
  arrival_time: ['5 minutes after 9', '9:05', 'five minutes after'],
  caregiver_back: ['hello', 'hi', 'back on phone'],
  acknowledgment: ['okay', 'understood', 'got it'],
  app_fault: ['apps fault', 'app fault', 'application fault'],
  errand_for_client: ['picked up something', 'errand', 'groceries', 'medicine'],
  will_try: ['okay', 'will try', 'try again'],
  cant_clock_in: ['cant', 'can\'t', 'wont allow', 'won\'t allow'],
  will_do: ['sorry', 'wasn\'t aware', 'will do'],
  client_wont_allow: ['client won\'t allow', 'client wont allow', 'cant use phone'],
  app_issue: ['app doesn\'t work', 'app doesnt work', 'my app'],
  client_new_number: ['client new number', 'new phone', 'client\'s new'],
  client_greeting: ['fine', 'good', 'doing well']
}; 