"""
Parse all Anbennar EU4 event modifiers into a JSON lookup.
Reads modifier definitions and their effects, plus localisation for display names.
"""
import os
import re
import json
import glob

MOD_PATH = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\236850\1385440355"
MODIFIER_DIR = os.path.join(MOD_PATH, "common", "event_modifiers")
LOCALISATION_DIR = os.path.join(MOD_PATH, "localisation")
OUTPUT = os.path.join(os.path.dirname(__file__), "modifiers_data.json")

# Human-readable names for common modifier effects
EFFECT_NAMES = {
    'manpower_recovery_speed': 'Manpower Recovery Speed',
    'global_manpower_modifier': 'National Manpower Modifier',
    'manpower_in_true_faith_provinces': 'Manpower in True Faith Provinces',
    'land_forcelimit': 'Land Force Limit',
    'land_forcelimit_modifier': 'Land Force Limit Modifier',
    'naval_forcelimit': 'Naval Force Limit',
    'naval_forcelimit_modifier': 'Naval Force Limit Modifier',
    'global_regiment_cost': 'Regiment Cost',
    'global_ship_cost': 'Ship Cost',
    'land_maintenance_modifier': 'Land Maintenance Modifier',
    'naval_maintenance_modifier': 'Naval Maintenance Modifier',
    'global_tax_modifier': 'National Tax Modifier',
    'production_efficiency': 'Production Efficiency',
    'trade_efficiency': 'Trade Efficiency',
    'global_trade_power': 'Global Trade Power',
    'trade_steering': 'Trade Steering',
    'merchants': 'Merchants',
    'colonists': 'Colonists',
    'diplomats': 'Diplomats',
    'missionaries': 'Missionaries',
    'discipline': 'Discipline',
    'morale_of_armies': 'Morale of Armies',
    'morale_of_navies': 'Morale of Navies',
    'infantry_combat_ability': 'Infantry Combat Ability',
    'cavalry_combat_ability': 'Cavalry Combat Ability',
    'artillery_combat_ability': 'Artillery Combat Ability',
    'heavy_ship_combat_ability': 'Heavy Ship Combat Ability',
    'light_ship_combat_ability': 'Light Ship Combat Ability',
    'galley_combat_ability': 'Galley Combat Ability',
    'siege_ability': 'Siege Ability',
    'fort_maintenance_modifier': 'Fort Maintenance',
    'defensiveness': 'Fort Defense',
    'garrison_size': 'Garrison Size',
    'global_autonomy': 'Monthly Autonomy Change',
    'stability_cost_modifier': 'Stability Cost Modifier',
    'advisor_cost': 'Advisor Cost',
    'advisor_pool': 'Possible Advisors',
    'diplomatic_reputation': 'Diplomatic Reputation',
    'improve_relation_modifier': 'Improve Relations',
    'ae_impact': 'Aggressive Expansion Impact',
    'core_creation': 'Core-Creation Cost',
    'province_warscore_cost': 'Province Warscore Cost',
    'prestige': 'Yearly Prestige',
    'prestige_decay': 'Prestige Decay',
    'legitimacy': 'Yearly Legitimacy',
    'republican_tradition': 'Yearly Republican Tradition',
    'devotion': 'Yearly Devotion',
    'horde_unity': 'Yearly Horde Unity',
    'meritocracy': 'Yearly Meritocracy',
    'technology_cost': 'Technology Cost',
    'idea_cost': 'Idea Cost',
    'innovativeness_gain': 'Innovativeness Gain',
    'embracement_cost': 'Institution Embracement Cost',
    'global_institution_spread': 'Institution Spread',
    'institution_spread_from_true_faith': 'Institution Spread from True Faith',
    'global_missionary_strength': 'Missionary Strength',
    'tolerance_own': 'Tolerance of the True Faith',
    'tolerance_heretic': 'Tolerance of Heretics',
    'tolerance_heathen': 'Tolerance of Heathens',
    'global_unrest': 'National Unrest',
    'local_unrest': 'Local Unrest',
    'local_tax_modifier': 'Local Tax Modifier',
    'local_production_efficiency': 'Local Production Efficiency',
    'local_manpower_modifier': 'Local Manpower Modifier',
    'local_development_cost': 'Local Development Cost',
    'local_build_cost': 'Local Construction Cost',
    'local_defensiveness': 'Local Defensiveness',
    'local_missionary_strength': 'Local Missionary Strength',
    'local_autonomy': 'Local Autonomy',
    'trade_goods_size_modifier': 'Local Goods Produced Modifier',
    'trade_goods_size': 'Local Goods Produced',
    'trade_value_modifier': 'Trade Value Modifier',
    'province_trade_power_modifier': 'Provincial Trade Power Modifier',
    'province_trade_power_value': 'Provincial Trade Power',
    'supply_limit_modifier': 'Supply Limit Modifier',
    'attrition': 'Attrition',
    'hostile_attrition': 'Hostile Attrition',
    'war_exhaustion': 'Monthly War Exhaustion',
    'war_exhaustion_cost': 'War Exhaustion Cost',
    'development_cost': 'Development Cost',
    'build_cost': 'Construction Cost',
    'inflation_reduction': 'Yearly Inflation Reduction',
    'interest': 'Interest per Annum',
    'global_colonial_growth': 'Global Settler Increase',
    'colonist_placement_chance': 'Colonist Chance',
    'range': 'Colonial Range',
    'spy_offence': 'Spy Network Construction',
    'global_spy_defence': 'Foreign Spy Detection',
    'liberty_desire': 'Liberty Desire in Subjects',
    'reduced_liberty_desire': 'Liberty Desire',
    'years_of_nationalism': 'Years of Separatism',
    'num_accepted_cultures': 'Max Promoted Cultures',
    'cultural_union_effect': 'Cultural Union Effect',
    'reform_progress_growth': 'Reform Progress Growth',
    'monthly_reform_progress_modifier': 'Monthly Reform Progress',
    'global_goods_produced_modifier': 'Goods Produced Modifier',
    'army_tradition': 'Yearly Army Tradition',
    'army_tradition_decay': 'Army Tradition Decay',
    'navy_tradition': 'Yearly Navy Tradition',
    'navy_tradition_decay': 'Navy Tradition Decay',
    'shock_damage': 'Shock Damage',
    'shock_damage_received': 'Shock Damage Received',
    'fire_damage': 'Fire Damage',
    'fire_damage_received': 'Fire Damage Received',
    'recover_army_morale_speed': 'Morale Recovery Speed',
    'reinforce_speed': 'Reinforce Speed',
    'movement_speed': 'Movement Speed',
    'global_regiment_recruit_speed': 'Recruitment Time',
    'global_ship_recruit_speed': 'Shipbuilding Time',
    'war_taxes_cost_modifier': 'War Taxes Cost',
    'leader_land_fire': 'Leader Fire',
    'leader_land_shock': 'Leader Shock',
    'leader_land_manuever': 'Leader Maneuver',
    'leader_land_siege': 'Leader Siege',
    'leader_naval_fire': 'Admiral Fire',
    'leader_naval_shock': 'Admiral Shock',
    'leader_naval_manuever': 'Admiral Maneuver',
    'power_projection_from_insults': 'Power Projection from Insults',
    'yearly_corruption': 'Yearly Corruption',
    'monthly_splendor': 'Monthly Splendor',
    'absolutism': 'Yearly Absolutism',
    'max_absolutism': 'Max Absolutism',
    'governing_capacity_modifier': 'Governing Capacity Modifier',
    'governing_capacity': 'Governing Capacity',
    'state_maintenance_modifier': 'State Maintenance',
    'administrative_efficiency': 'Administrative Efficiency',
    'mercenary_cost': 'Mercenary Cost',
    'merc_maintenance_modifier': 'Mercenary Maintenance',
    'available_province_loot': 'Available Province Loot',
    'loot_amount': 'Loot Amount',
    'army_professionalism': 'Army Professionalism',
    'drill_gain_modifier': 'Drill Gain Modifier',
    'drill_decay_modifier': 'Drill Decay Modifier',
    'reserves_organisation': 'Reserves Organisation',
    'special_unit_forcelimit': 'Special Unit Force Limit',
    'amount_of_banners': 'Amount of Banners',
    'Church_power_modifier': 'Church Power Modifier',
    'monthly_piety': 'Monthly Piety',
    'monthly_karma': 'Monthly Karma',
    'monthly_fervor_increase': 'Monthly Fervor Increase',
    'harmonization_speed': 'Harmonization Speed',
    'church_power_modifier': 'Church Power Modifier',
    'papal_influence': 'Yearly Papal Influence',
    'curia_treasury_contribution': 'Curia Treasury Contribution',
    'relation_with_heretics': 'Relations with Heretics',
    'warscore_cost_vs_other_religion': 'Warscore Cost vs Other Religions',
    'cb_on_religious_enemies': 'CB on Religious Enemies',
    'may_recruit_female_generals': 'May Recruit Female Generals',
    'heir_chance': 'Chance of New Heir',
    'female_advisor_chance': 'Female Advisor Chance',
    'allowed_marine_fraction': 'Marines Force Limit',
    'flagship_cost': 'Flagship Cost',
    'center_of_trade_upgrade_cost': 'Center of Trade Upgrade Cost',
    'caravan_power': 'Caravan Power',
    'global_prosperity_growth': 'Prosperity Growth',
    'monthly_gold_inflation_modifier': 'Gold Inflation',
    'envoy_travel_time': 'Envoy Travel Time',
    'backrow_artillery_damage': 'Artillery Damage from Back Row',
    'country_military_power': 'Monthly Military Power',
    'country_admin_power': 'Monthly Administrative Power',
    'country_diplomatic_power': 'Monthly Diplomatic Power',
    'all_power_cost': 'All Power Costs',
    'free_adm_policy': 'Free Admin Policy',
    'free_dip_policy': 'Free Diplomatic Policy',
    'free_mil_policy': 'Free Military Policy',
    'possible_adm_policy': 'Possible Administrative Policies',
    'possible_dip_policy': 'Possible Diplomatic Policies',
    'possible_mil_policy': 'Possible Military Policies',
    'max_states': 'Max States',
    'num_of_parliament_issues': 'Number of Parliament Issues',
    'global_heretic_missionary_strength': 'Missionary Strength vs Heretics',
    'auto_explore_adjacent_to_colony': 'Auto-Explore Adjacent to Colony',
    'cb_on_primitives': 'CB on Primitives',
    'can_fabricate_for_vassals': 'Can Fabricate for Vassals',
    'attack_bonus_in_capital_terrain': 'Attack Bonus in Capital Terrain',
    'movement_speed_onto_off_boat_modifier': 'Disembark Speed',
    'vassal_income': 'Income from Vassals',
    'migration_cooldown': 'Migration Cooldown',
    'native_uprising_chance': 'Native Uprising Chance',
    'native_assimilation': 'Native Assimilation',
    'ship_durability': 'Ship Durability',
    'capture_ship_chance': 'Ship Capture Chance',
    'sunk_ship_morale_hit_recieved': 'Sunk Ship Morale Hit',
    'blockade_efficiency': 'Blockade Efficiency',
    'embargo_efficiency': 'Embargo Efficiency',
    'privateer_efficiency': 'Privateer Efficiency',
    'global_naval_engagement_modifier': 'Naval Engagement Modifier',
    'local_colonial_growth': 'Local Settler Increase',
    'local_hostile_attrition': 'Local Hostile Attrition',
    'local_friendly_movement_speed': 'Local Friendly Movement Speed',
    'local_hostile_movement_speed': 'Local Hostile Movement Speed',
    'local_supply_limit_modifier': 'Local Supply Limit',
    'local_sailors_modifier': 'Local Sailors Modifier',
    'local_ship_repair': 'Local Ship Repair',
    'province_has_center_of_trade_of_level': None,  # not an effect
    'picture': None,  # icon reference
    'key': None,
    'desc': None,
    'religion': None,
    'religion_group': None,
    'potential': None,
    'trigger': None,
}

def format_value(val):
    """Format a modifier value for display"""
    try:
        f = float(val)
        if abs(f) < 1 and f != 0:
            # Percentage
            return f"{f*100:+.1f}%".rstrip('0').rstrip('.')  + '%' if not f"{f*100:+.1f}".endswith('%') else f"{f*100:+.1f}%"
        else:
            return f"{f:+g}"
    except:
        return val

def format_value_nice(key, val):
    """Format value with sign and percentage if needed"""
    try:
        f = float(val)
        # Most modifiers are percentages when < 1 (with some exceptions)
        percent_keys = {
            'manpower_recovery_speed', 'global_manpower_modifier', 'production_efficiency',
            'trade_efficiency', 'global_trade_power', 'trade_steering', 'discipline',
            'morale_of_armies', 'morale_of_navies', 'infantry_combat_ability',
            'cavalry_combat_ability', 'artillery_combat_ability', 'siege_ability',
            'defensiveness', 'garrison_size', 'global_autonomy', 'stability_cost_modifier',
            'advisor_cost', 'improve_relation_modifier', 'ae_impact', 'core_creation',
            'province_warscore_cost', 'technology_cost', 'idea_cost', 'global_missionary_strength',
            'local_tax_modifier', 'local_production_efficiency', 'local_manpower_modifier',
            'local_development_cost', 'local_build_cost', 'local_defensiveness',
            'development_cost', 'build_cost', 'trade_goods_size_modifier',
            'trade_value_modifier', 'province_trade_power_modifier', 'supply_limit_modifier',
            'reform_progress_growth', 'global_goods_produced_modifier',
            'shock_damage', 'shock_damage_received', 'fire_damage', 'fire_damage_received',
            'recover_army_morale_speed', 'reinforce_speed', 'movement_speed',
            'global_regiment_recruit_speed', 'global_ship_recruit_speed',
            'land_forcelimit_modifier', 'naval_forcelimit_modifier',
            'land_maintenance_modifier', 'naval_maintenance_modifier',
            'global_regiment_cost', 'global_ship_cost', 'mercenary_cost',
            'merc_maintenance_modifier', 'fort_maintenance_modifier',
            'embracement_cost', 'governing_capacity_modifier', 'state_maintenance_modifier',
            'administrative_efficiency', 'colonist_placement_chance',
            'monthly_reform_progress_modifier', 'war_exhaustion_cost',
            'inflation_reduction', 'yearly_corruption', 'prestige_decay',
            'army_tradition_decay', 'navy_tradition_decay',
            'local_missionary_strength', 'local_hostile_attrition',
            'local_sailors_modifier',
            'monthly_gold_inflation_modifier', 'center_of_trade_upgrade_cost',
            'envoy_travel_time', 'all_power_cost',
            'local_autonomy',
        }
        if key in percent_keys or (abs(f) < 1 and abs(f) > 0 and key not in {'prestige', 'legitimacy', 'republican_tradition', 'devotion', 'horde_unity', 'meritocracy', 'army_tradition', 'navy_tradition', 'war_exhaustion', 'absolutism', 'monthly_splendor', 'monthly_piety', 'monthly_karma', 'monthly_fervor_increase', 'papal_influence'}):
            pct = f * 100
            return f"{pct:+.1f}%".replace('.0%', '%')
        else:
            if f == int(f):
                return f"{int(f):+d}"
            return f"{f:+.2f}"
    except:
        return str(val)


def parse_modifier_file(filepath):
    """Parse a Paradox modifier file and return dict of modifier_name -> {effects}"""
    modifiers = {}
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            text = f.read()
    except:
        return modifiers

    # Remove comments
    text = re.sub(r'#[^\n]*', '', text)

    # Parse top-level blocks: modifier_name = { ... }
    i = 0
    while i < len(text):
        # Find next identifier at start of line (after whitespace)
        m = re.match(r'\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\{', text[i:])
        if not m:
            i += 1
            continue

        name = m.group(1)
        brace_start = i + m.end() - 1

        # Find matching closing brace
        depth = 1
        j = brace_start + 1
        while j < len(text) and depth > 0:
            if text[j] == '{':
                depth += 1
            elif text[j] == '}':
                depth -= 1
            j += 1

        inner = text[brace_start+1:j-1]

        # Parse effects from the inner block (only top-level key = value pairs)
        effects = {}
        for line in inner.split('\n'):
            line = line.strip()
            em = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', line)
            if em:
                ekey = em.group(1)
                eval_str = em.group(2).strip()
                # Skip nested blocks and meta keys
                if '{' in eval_str:
                    continue
                if ekey in ('picture', 'key', 'desc', 'religion', 'religion_group', 'potential', 'trigger'):
                    continue
                effects[ekey] = eval_str

        if effects:
            modifiers[name] = effects

        i = j

    return modifiers


def load_localisation():
    """Load localisation strings for modifier names"""
    loc = {}
    loc_dir = LOCALISATION_DIR
    if not os.path.exists(loc_dir):
        return loc

    for filepath in glob.glob(os.path.join(loc_dir, '*_l_english.yml')):
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    m = re.match(r'^\s*([a-zA-Z0-9_]+):\d*\s+"(.+)"', line)
                    if m:
                        loc[m.group(1)] = m.group(2)
        except:
            continue

    return loc


def main():
    all_modifiers = {}

    # Parse all modifier files
    for filepath in glob.glob(os.path.join(MODIFIER_DIR, '*.txt')):
        mods = parse_modifier_file(filepath)
        all_modifiers.update(mods)

    print(f"Parsed {len(all_modifiers)} modifiers from {len(glob.glob(os.path.join(MODIFIER_DIR, '*.txt')))} files")

    # Load localisation
    loc = load_localisation()
    print(f"Loaded {len(loc)} localisation strings")

    # Build output: modifier_name -> { display_name, effects: [{name, value, raw_key}] }
    output = {}
    for mod_name, effects in all_modifiers.items():
        display_name = loc.get(mod_name, mod_name.replace('_', ' ').title())

        effect_list = []
        for ekey, eval_str in effects.items():
            ename = EFFECT_NAMES.get(ekey, ekey.replace('_', ' ').title())
            if ename is None:
                continue  # Skip meta keys
            formatted = format_value_nice(ekey, eval_str)
            effect_list.append({
                'name': ename,
                'value': formatted,
                'key': ekey,
            })

        if effect_list:
            output[mod_name] = {
                'name': display_name,
                'effects': effect_list,
            }

    # Write output
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, separators=(',', ':'))

    print(f"Written {len(output)} modifiers to {OUTPUT}")

    # Show some examples
    for example in ['command_swords_and_dumplings', 'command_obedient_zanyu_kikunin', 'hobgoblin_zanyu_kikun']:
        if example in output:
            print(f"\n{example}: {output[example]}")
        else:
            print(f"\n{example}: NOT FOUND")


if __name__ == '__main__':
    main()
