# Timing specification

---

Timing information can be specified in the following places:

- Showing a screen for a given duration:

        show Introduction for 10000

- Displaying a component during the test run for a given duration:

        cross() for 1000

- Defining when the component should be shown. For this we use component timing
  expression which is specified before the component. For example:
  
        at .+200 rectangle()
  
  
    This is the general form of the timing expression:
  
        at <target:><.><+ or -><miliseconds>
       
    where: 
   
    - `target:` - is the name of the component this expression is relative to. If
      not given, timing expression is relative to the previous component.
    - `.` means relative to the start of the target component. If not given time
      is relative to the end of the previous component.
    - `+` or `-` - specified time is relative and is added or subtracted from the
      target time.
    - `<miliseconds>` - a number of miliseconds
    
    If timing expression is not given for the component, by default it is:
    
          at .
          
    which means start at the same time as the previous component.
       
    Examples:
  
          at 200 cross()           --  show cross 200ms after the phase begins (this is absolute time)
          at .-100 cross()         -- show cross 100ms before the start of the previous component
          at +100 cross()          -- show cross 100ms after the finish of the previous component
          at myrec:.+100 cross()   -- show cross 100ms after the start of the myrec component
          at myrec:+100 cross()    -- show cross 100ms after the finish of the myrec component
          at myrec:-100 cross()    -- show cross 100ms before the finish of the myrec component


     
