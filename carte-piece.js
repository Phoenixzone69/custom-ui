import {
  LitElement,
  html,
  css
} from "https://unpkg.com/lit-element@2.0.1/lit-element.js?module";

console.info(
  `%c CARTE-PIECE %c ${'5.1.0'} `,
  'color: white; background: #2c3e50; font-weight: 700;',
  'color: #2c3e50; background: white; font-weight: 700;',
);

const fireEvent = (node, type, detail, options) => {
  options = options || {};
  detail = detail === null || detail === undefined ? {} : detail;
  const event = new Event(type, {
    bubbles: options.bubbles === undefined ? true : options.bubbles,
    cancelable: Boolean(options.cancelable),
    composed: options.composed === undefined ? true : options.composed,
  });
  event.detail = detail;
  node.dispatchEvent(event);
  return event;
};

// --- EDITOR ---
class CartePieceEditor extends LitElement {
  static get properties() {
    return { hass: {}, _config: {} };
  }

  setConfig(config) {
    this._config = config || {};
  }

  _valueChanged(ev) {
    if (!this.hass) return;
    const { target } = ev;
    const newConfig = { ...this._config };
    const configValue = target.configValue;

    if (configValue) {
      let value = target.value;
      if (target.checked !== undefined) {
        value = target.checked;
      }

      if (value === '' || value === null || value === undefined) {
        delete newConfig[configValue];
      } else {
        newConfig[configValue] = value;
      }
    }

    fireEvent(this, "config-changed", { config: newConfig });
  }

  _renderButtonEditor(index) {
    const entityConfig = `button${index}_entity`;
    const nameConfig = `button${index}_name`;
    const showIconConfig = `button${index}_show_icon`;
    const showNameConfig = `button${index}_show_name`;
    const showStateConfig = `button${index}_show_state`;

    return html`
      <div class="button-editor-section">
        <h4>Bouton d'action ${index}</h4>
        <ha-entity-picker
          label="Entité"
          .hass=${this.hass}
          .value=${this._config[entityConfig] || ''}
          .configValue=${entityConfig}
          @value-changed=${this._valueChanged}
        ></ha-entity-picker>

        ${this._config[entityConfig] ? html`
          <ha-textfield
            label="Nom personnalisé (optionnel)"
            .value=${this._config[nameConfig] || ''}
            .configValue=${nameConfig}
            @input=${this._valueChanged}
            class="full-width"
          ></ha-textfield>
          <div class="side-by-side">
            <ha-formfield label="Icône">
              <ha-switch
                .checked=${this._config[showIconConfig] !== false}
                .configValue=${showIconConfig}
                @change=${this._valueChanged}
              ></ha-switch>
            </ha-formfield>
            <ha-formfield label="Nom">
              <ha-switch
                .checked=${this._config[showNameConfig] !== false}
                .configValue=${showNameConfig}
                @change=${this._valueChanged}
              ></ha-switch>
            </ha-formfield>
            <ha-formfield label="État">
              <ha-switch
                .checked=${this._config[showStateConfig] === true}
                .configValue=${showStateConfig}
                @change=${this._valueChanged}
              ></ha-switch>
            </ha-formfield>
          </div>
        ` : ''}
      </div>
    `;
  }

  render() {
    if (!this.hass || !this._config) return html``;

    const showActionButtons = this._config.show_action_buttons || false;

    return html`
      <div class="card-config">
        <h3>Configuration Principale</h3>
        <ha-area-picker
          label="Zone de la pièce"
          .hass=${this.hass}
          .value="${this._config.area || ''}"
          .configValue=${"area"}
          @value-changed=${this._valueChanged}
        ></ha-area-picker>
        <ha-formfield label="Afficher les informations au-dessus de l'image ?">
          <ha-switch
            .checked=${this._config.info_above_image || false}
            .configValue=${"info_above_image"}
            @change=${this._valueChanged}
          ></ha-switch>
        </ha-formfield>

        <ha-formfield label="Afficher la température ?">
          <ha-switch
            .checked=${this._config.show_temp || false}
            .configValue=${"show_temp"}
            @change=${this._valueChanged}
          ></ha-switch>
        </ha-formfield>
        ${this._config.show_temp ? html`
          <ha-entity-picker
            label="Capteur de température"
            .hass=${this.hass}
            .value="${this._config.temp_entity || ''}"
            .configValue=${"temp_entity"}
            @value-changed=${this._valueChanged}
            .includeDomains=${['sensor']}
          ></ha-entity-picker>
        ` : ''}

        <ha-formfield label="Afficher l'humidité ?">
          <ha-switch
            .checked=${this._config.show_humid || false}
            .configValue=${"show_humid"}
            @change=${this._valueChanged}
          ></ha-switch>
        </ha-formfield>
        ${this._config.show_humid ? html`
          <ha-entity-picker
            label="Capteur d'humidité"
            .hass=${this.hass}
            .value="${this._config.humid_entity || ''}"
            .configValue=${"humid_entity"}
            @value-changed=${this._valueChanged}
            .includeDomains=${['sensor']}
          ></ha-entity-picker>
        ` : ''}

        <h3>Affichage Média</h3>
        <ha-select
          label="Type d'affichage"
          .value=${this._config.display_type || 'image'}
          .configValue=${"display_type"}
          @selected=${this._valueChanged}
          @closed=${(ev) => ev.stopPropagation()}
        >
          <mwc-list-item value="image">Image</mwc-list-item>
          <mwc-list-item value="compact">Compact (sans image)</mwc-list-item>
          <mwc-list-item value="video">Flux Vidéo</mwc-list-item>
          <mwc-list-item value="graph">Graphique Température</mwc-list-item>
        </ha-select>

        ${this._config.display_type === 'video' ? html`
          <ha-entity-picker
            label="Entité Caméra"
            .hass=${this.hass}
            .value="${this._config.camera_entity || ''}"
            .configValue=${"camera_entity"}
            @value-changed=${this._valueChanged}
            .includeDomains=${['camera']}
          ></ha-entity-picker>
        ` : ''}

        <h3>Boutons d'action</h3>
        <ha-formfield label="Activer les boutons d'action ?">
          <ha-switch
            .checked=${showActionButtons}
            .configValue=${"show_action_buttons"}
            @change=${this._valueChanged}
          ></ha-switch>
        </ha-formfield>
        ${showActionButtons ? html`
          ${[1, 2, 3, 4].map(i => this._renderButtonEditor(i))}
        ` : ''}
      </div>
    `;
  }

  static get styles() {
    return css`
      .card-config { display: flex; flex-direction: column; gap: 8px; }
      h3 { margin-bottom: 0; margin-top: 16px; }
      h4 { margin-top: 16px; margin-bottom: 4px; font-size: 1.1em; }
      .button-editor-section {
        border: 1px solid var(--divider-color);
        padding: 8px;
        border-radius: 4px;
        margin-top: 8px;
      }
      .side-by-side {
        display: flex;
        gap: 16px;
        align-items: center;
        flex-wrap: wrap;
      }
      .full-width {
        width: 100%;
      }
    `;
  }
}
customElements.define('carte-piece-editor', CartePieceEditor);


// --- CARD ---
class CartePiece extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object },
      _areaName: { state: true },
      _areaIcon: { state: true },
      _areaPicture: { state: true },
    };
  }

  setConfig(config) {
    this.config = config;
    if (this.hass) {
        this._updateAreaData();
    }
  }

  set hass(hass) {
    this._hass = hass;
    this._updateAreaData();
  }

  _updateAreaData() {
    if (!this.config || !this._hass || !this.config.area) {
      this._areaName = 'Pièce';
      this._areaIcon = 'mdi:home';
      this._areaPicture = null;
      this.requestUpdate();
      return;
    }

    const areaId = this.config.area;
    const area = this._hass.areas[areaId];

    this._areaName = area ? area.name : 'Pièce';
    this._areaIcon = area ? area.icon || 'mdi:home' : 'mdi:home';
    this._areaPicture = area ? area.picture || null : null;

    this.requestUpdate();
  }

  getCardSize() {
    const displayType = this.config.display_type || 'image';
    if (displayType === 'compact') {
      return 1;
    }
    return 3;
  }

  _handleTap(entityId) {
    this._hass.callService("homeassistant", "toggle", {
      entity_id: entityId,
    });
  }

  _renderMedia() {
    const displayType = this.config.display_type || 'image';

    switch (displayType) {
      case 'compact':
        return html``;

      case 'video':
        if (this.config.camera_entity) {
          return html`<hui-image
            .hass=${this._hass}
            .cameraImage=${this.config.camera_entity}
            .cameraView=${"live"}
          ></hui-image>`;
        }
        return html`<ha-alert alert-type="warning">Aucune entité caméra sélectionnée.</ha-alert>`;

      case 'graph':
        if (this.config.show_temp && this.config.temp_entity) {
          return html`<ha-history-graph
            .hass=${this._hass}
            .entities=${[this.config.temp_entity]}
            .hoursToShow=${24}
            .refreshInterval=${0}
          ></ha-history-graph>`;
        }
        return html`<ha-alert alert-type="warning">Aucun capteur de température sélectionné.</ha-alert>`;

      case 'image':
      default:
        if (this._areaPicture) {
          return html`<img class="room-image" src="${this._areaPicture}" alt="Image de la pièce" />`;
        }
        return html``;
    }
  }

  render() {
    if (!this.config || !this._hass) return html``;

    const infoAbove = this.config.info_above_image || false;
    const showButtons = this.config.show_action_buttons || false;

    const showTemp = this.config.show_temp && this.config.temp_entity && this._hass.states[this.config.temp_entity];
    const showHumid = this.config.show_humid && this.config.humid_entity && this._hass.states[this.config.humid_entity];

    const tempStateObj = showTemp ? this._hass.states[this.config.temp_entity] : null;
    const humidStateObj = showHumid ? this._hass.states[this.config.humid_entity] : null;

    const tempState = tempStateObj ? `${tempStateObj.state}${tempStateObj.attributes.unit_of_measurement || ''}` : null;
    const humidState = humidStateObj ? `${humidStateObj.state}${humidStateObj.attributes.unit_of_measurement || ''}` : null;

    const content = html`
      <div class="info-grid">
        <ha-icon class="info-grid-icon" .icon=${this._areaIcon}></ha-icon>
        <span class="info-grid-name">${this._areaName}</span>
        <div class="info-grid-sensors">
          ${showTemp ? html`<span><ha-icon icon="mdi:thermometer"></ha-icon>${tempState}</span>` : ''}
          ${showHumid ? html`<span><ha-icon icon="mdi:water-percent"></ha-icon>${humidState}</span>` : ''}
        </div>
      </div>
    `;

    const buttons = [];
    if (showButtons && this._hass) {
      for (let i = 1; i <= 4; i++) {
        const entityId = this.config[`button${i}_entity`];
        if (entityId && this._hass.states[entityId]) {
          const stateObj = this._hass.states[entityId];

          const showIcon = this.config[`button${i}_show_icon`] !== false;
          const showName = this.config[`button${i}_show_name`] !== false;
          const showState = this.config[`button${i}_show_state`] === true;
          const customName = this.config[`button${i}_name`];
          const name = customName || stateObj.attributes.friendly_name;

          buttons.push(html`
            <div class="action-button" @click=${() => this._handleTap(entityId)} title="${name}">
              ${showIcon ? html`<ha-state-icon .stateObj=${stateObj} .stateColor=${true}></ha-state-icon>`: ''}
              ${showName || showState ? html`
                <div class="button-text">
                  ${showName ? html`<span class="button-name">${name}</span>` : ''}
                  ${showState ? html`<span class="button-state">${stateObj.state} ${stateObj.attributes.unit_of_measurement || ''}</span>` : ''}
                </div>
              ` : ''}
            </div>
          `);
        }
      }
    }

    const mediaContent = this._renderMedia();

    return html`
      <ha-card>
        <div class="container">
          ${infoAbove ? html`${content}` : ''}
          ${mediaContent ? html`<div class="media-content">${mediaContent}</div>` : ''}
          ${!infoAbove ? html`${content}` : ''}
          ${buttons.length > 0 ? html`
            <div class="action-buttons">
              ${buttons}
            </div>
          ` : ''}
        </div>
      </ha-card>
    `;
  }

  static get styles() {
    return css`
      :host { display: block; }
      .container {
        padding: 16px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
      }
      .info-grid {
        display: grid;
        width: 100%;
        grid-template-areas:
          "i n"
          "i s";
        grid-template-columns: min-content 1fr;
        grid-template-rows: min-content min-content;
        gap: 0px 12px;
        align-items: center;
        text-align: left;
      }
      .info-grid-icon {
        grid-area: i;
        --mdc-icon-size: 40px;
      }
      .info-grid-name {
        grid-area: n;
        font-size: 1.4em;
        font-weight: bold;
      }
      .info-grid-sensors {
        grid-area: s;
        display: flex;
        gap: 16px;
        font-size: 0.9em;
        color: var(--secondary-text-color);
      }
      .info-grid-sensors span {
        display: flex;
        align-items: center;
        gap: 4px;
      }
      .info-grid-sensors ha-icon {
        --mdc-icon-size: 18px;
      }
      .media-content {
        width: 100%;
        height: auto;
        border-radius: 12px;
        overflow: hidden;
      }
      .media-content > * {
        width: 100%;
        display: block;
      }
      .room-image {
        width: 100%;
        height: auto;
        display: block;
      }
      .action-buttons {
        display: flex;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
        align-items: stretch;
      }
      .action-button {
        cursor: pointer;
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-sizing: border-box;
        height: auto;
        min-height: 27px;
        padding: 4px 8px;
        line-height: 1.2;
        border-radius: 10px;
        border-color: rgba(0, 0, 0, 0.1);
        border-style: outset;
        border-width: 1px;
      }
      .action-button ha-state-icon {
        width: 14px;
        filter: drop-shadow(1px 2px 1px rgba(0,0,0,0.3));
      }
      .button-text {
        display: flex;
        flex-direction: column;
        margin-top: 4px;
        text-align: center;
      }
      .button-name {
        font-size: 12px;
        font-weight: bold;
        color: var(--primary-text-color);
      }
      .button-state {
        font-size: 11px;
        color: var(--secondary-text-color);
      }
      .card-config { display: flex; flex-direction: column; gap: 8px; }
      h3 { margin-bottom: 0; margin-top: 16px; }
    `;
  }

  static getConfigElement() {
    return document.createElement("carte-piece-editor");
  }
}
customElements.define('carte-piece', CartePiece);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "carte-piece",
  name: "Carte Pièce",
  preview: true,
  description: "Une carte personnalisée pour une pièce, avec auto-détection par zone.",
});
