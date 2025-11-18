import { useState, useEffect } from 'react';
import DatePickerLib from 'react-datepicker';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import 'react-datepicker/dist/react-datepicker.css';
import { Input } from './ui/input';
import { cn } from './ui/utils';

interface DatePickerProps {
  value?: Date;
  onChange: (date: Date | undefined) => void;
  minYear?: number;
  maxYear?: number;
  label?: string;
  placeholder?: string;
  disabled?: boolean;
}

export const DatePicker = ({ 
  value, 
  onChange, 
  minYear = 1900, 
  maxYear = new Date().getFullYear(),
  label,
  placeholder = "Selecione a data",
  disabled = false
}: DatePickerProps) => {
  const [selectedDate, setSelectedDate] = useState<Date | null>(value || null);

  useEffect(() => {
    setSelectedDate(value || null);
  }, [value]);

  const handleDateChange = (date: Date | null) => {
    setSelectedDate(date);
    onChange(date || undefined);
  };

  return (
    <div className="space-y-2">
      {label && (
        <label className="text-sm font-medium text-foreground">{label}</label>
      )}
      <div className="relative">
        <DatePickerLib
          selected={selectedDate}
          onChange={handleDateChange}
          dateFormat="dd/MM/yyyy"
          locale={ptBR}
          showYearDropdown
          showMonthDropdown
          dropdownMode="select"
          yearDropdownItemNumber={maxYear - minYear + 1}
          minDate={new Date(minYear, 0, 1)}
          maxDate={new Date()}
          disabled={disabled}
          placeholderText={placeholder}
          className={cn(
            "flex h-9 w-full rounded-md border border-[var(--input-border)] bg-input-background px-3 py-1 text-sm transition-colors",
            "file:border-0 file:bg-transparent file:text-sm file:font-medium",
            "placeholder:text-muted-foreground",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/20 focus-visible:border-[var(--input-border-active)]",
            "disabled:cursor-not-allowed disabled:opacity-50",
            "w-full"
          )}
          customInput={
            <Input
              value={selectedDate ? format(selectedDate, "dd 'de' MMMM 'de' yyyy", { locale: ptBR }) : ''}
              placeholder={placeholder}
              readOnly
              disabled={disabled}
              className="cursor-pointer"
            />
          }
          renderCustomHeader={({
            date,
            changeYear,
            changeMonth,
            decreaseMonth,
            increaseMonth,
            prevMonthButtonDisabled,
            nextMonthButtonDisabled,
          }) => (
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <button
                onClick={decreaseMonth}
                disabled={prevMonthButtonDisabled}
                type="button"
                className={cn(
                  "rounded-md p-1 hover:bg-accent/10 transition-colors",
                  prevMonthButtonDisabled && "opacity-50 cursor-not-allowed"
                )}
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M10 12L6 8L10 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
              
              <div className="flex items-center gap-2">
                <select
                  value={date.getMonth()}
                  onChange={({ target: { value } }) => changeMonth(parseInt(value, 10))}
                  className="bg-transparent border border-border rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-accent/20"
                >
                  {[
                    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
                  ].map((month, index) => (
                    <option key={index} value={index}>
                      {month}
                    </option>
                  ))}
                </select>
                
                <select
                  value={date.getFullYear()}
                  onChange={({ target: { value } }) => changeYear(parseInt(value, 10))}
                  className="bg-transparent border border-border rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-accent/20"
                >
                  {Array.from({ length: maxYear - minYear + 1 }, (_, i) => maxYear - i).map((year) => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  ))}
                </select>
              </div>
              
              <button
                onClick={increaseMonth}
                disabled={nextMonthButtonDisabled}
                type="button"
                className={cn(
                  "rounded-md p-1 hover:bg-accent/10 transition-colors",
                  nextMonthButtonDisabled && "opacity-50 cursor-not-allowed"
                )}
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M6 4L10 8L6 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </div>
          )}
        />
      </div>
      
      {/* Display selected date */}
      {selectedDate && (
        <div className="text-sm text-secondary text-center">
          {format(selectedDate, "dd 'de' MMMM 'de' yyyy", { locale: ptBR })}
        </div>
      )}
    </div>
  );
};
