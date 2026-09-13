import { useState, type FormEvent } from "react";
import styles from "./Composer.module.css";

type ComposerProps = {
  placeholder: string;
  submitLabel: string;
  disabled?: boolean;
  onSubmit: (value: string) => void;
};

export function Composer({ placeholder, submitLabel, disabled = false, onSubmit }: ComposerProps) {
  const [value, setValue] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextValue = value.trim();
    if (!nextValue || disabled) {
      return;
    }

    onSubmit(nextValue);
    setValue("");
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <label className={styles.srOnly} htmlFor="composer-input">
        {placeholder}
      </label>
      <input
        id="composer-input"
        className={styles.input}
        value={value}
        placeholder={placeholder}
        autoComplete="off"
        disabled={disabled}
        onChange={(event) => setValue(event.target.value)}
      />
      <button className={styles.send} type="submit" disabled={disabled || value.trim().length === 0}>
        {submitLabel}
      </button>
    </form>
  );
}
